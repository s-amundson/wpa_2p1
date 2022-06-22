import uuid
from django import forms
from django.conf import settings
from square.client import Client

from ..models import Card, Customer, PaymentLog
from ..src import CardHelper, CustomerHelper

import logging
logger = logging.getLogger(__name__)


class PaymentForm(forms.ModelForm):
    amount = forms.IntegerField(required=True)
    card = forms.ChoiceField(required=True)
    donation_note = forms.CharField(widget=forms.Textarea, required=False)
    # items = forms.JSONField(widget=forms.HiddenInput())
    save_card = forms.BooleanField(required=False, initial=False, label='Save card for future purchases')
    source_id = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = PaymentLog
        fields = ('amount', 'card', 'donation', 'donation_note', 'save_card', 'source_id')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        logging.debug(user)
        if 'description' in kwargs:
            self.description = kwargs.pop('description')
        else:
            self.description = ''
        if 'line_items' in kwargs:
            self.line_items = kwargs.pop('line_items')
        else:
            self.line_items = []
        super().__init__(*args, **kwargs)

        # Create an instance of the API Client
        # and initialize it with the credentials
        # for the Square account whose assets you want to manage
        self.client = Client(
            access_token=settings.SQUARE_CONFIG['access_token'],
            environment=settings.SQUARE_CONFIG['environment'],
        )
        self.square_response = {'payment': None}
        self.donation_amount = 0
        self.donation_note = ''
        self.log = None
        self.user = user
        self.fields['card'].choices = self.card_choices()
        self.fields['donation_note'].widget.attrs.update({'cols': 30, 'rows': 3, 'class': 'form-control'})
        self.fields['save_card'].widget.attrs.update({'class': 'm-2 form-check-input'})
        self.payment_errors = []
        self.error_dict = {
            'CVV_FAILURE': 'Payment Error: CVV',
            'CARD_DECLINED_VERIFICATION_REQUIRED': 'Payment Error: Strong Autentication not supported at this time, please use a different card.',
            'GENERIC_DECLINE': 'Payment Error: Card Declined',
            'INVALID_EXPIRATION': 'Payment Error: Expiration Date',
            '': 'Payment Error'
        }

    def card_choices(self):
        if not self.user.is_authenticated:
            return [(0, "New Card")]
        saved_cards = Card.objects.filter(customer__user=self.user, enabled=True)
        card_choices = []
        for card in saved_cards:
            card_choices.append((card.id, str(card)))
        card_choices.append((0, "New Card"))
        logging.debug(card_choices)
        return card_choices

    def process_payment(self, idempotency_key, autocomplete=True):
        note = self.description
        if self.cleaned_data['donation'] > 0:
            note = note + f"Donation of {self.cleaned_data['donation']}"
        # logging.debug(type(self.cleaned_data['items']))
        # for item in self.cleaned_data['items']:
        #     logging.debug(type(item))
        #     note += f"{item.get('name')}, "
        logging.debug(self.cleaned_data)
        logging.debug(self.line_items)
        body = {
                "idempotency_key": idempotency_key,
                "amount_money": {"amount": self.cleaned_data['amount'] * 100, "currency": "USD"},
                "autocomplete": autocomplete,
                "location_id": settings.SQUARE_CONFIG['location_id'],
                "note": note[:250]
            }
        if self.cleaned_data['card'] != '0':
            card = Card.objects.get(pk=self.cleaned_data['card'])
            body['source_id'] = card.card_id
            body['customer_id'] = card.customer.customer_id
        else:
            body['source_id'] = self.cleaned_data['source_id']
        result = self.client.payments.create_payment(
            body=body
        )

        self.square_response = result.body.get('payment', {'payment': None})
        # logging.debug(self.square_response)
        if result.is_success():
            self.log = self.save(commit=False)
            if self.user.is_authenticated:
                self.log.user = self.user
            else:
                self.log.user = None
            self.log.checkout_created_time = self.square_response['created_at']
            self.log.description = note[:250]  # database set to 255 characters
            self.log.location_id = self.square_response['location_id']
            self.log.idempotency_key = idempotency_key
            self.log.order_id = self.square_response['order_id']
            self.log.payment_id = self.square_response['id']
            self.log.receipt = self.square_response['receipt_url']
            self.log.source_type = self.square_response['source_type']
            self.log.status = self.square_response['status']
            self.log.total_money = self.square_response['approved_money']['amount']
            self.log.save()

            if self.cleaned_data['save_card']:
                customer = Customer.objects.filter(user=self.user).last()
                logging.debug(customer)
                if customer is None:
                    ch = CustomerHelper(self.user)
                    customer = ch.create_customer()
                if customer is not None:
                    card_helper = CardHelper()
                    card = card_helper.create_card_from_payment(customer, self.log)
                    return card is not None
            return True

        elif result.is_error():
            logging.debug(result.errors)
            for error in result.errors:
                self.payment_errors.append(self.error_dict.get(error.get('code', ''), 'Payment Error'))
            logging.debug(self.payment_errors)
        return False
