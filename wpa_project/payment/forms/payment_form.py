from django import forms
from django.utils import timezone

from ..models import Card, Customer, PaymentLog
from ..src import CardHelper, CustomerHelper, EmailMessage, PaymentHelper

import logging
logger = logging.getLogger(__name__)


class PaymentForm(forms.ModelForm):
    amount = forms.IntegerField(required=True)
    card = forms.ChoiceField(required=True)
    donation_note = forms.CharField(widget=forms.Textarea, required=False)
    save_card = forms.BooleanField(required=False, initial=False, label='Save card for future purchases')
    source_id = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = PaymentLog
        fields = ('amount', 'card', 'category', 'donation', 'donation_note', 'save_card', 'source_id')

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
        self.amount_initial = kwargs.get('initial', {}).get('amount', 0)
        super().__init__(*args, **kwargs)

        self.square_response = {'payment': None}
        self.donation_amount = 0
        self.donation_note = ''
        self.log = None
        self.user = user
        self.fields['card'].choices = self.card_choices()
        self.fields['category'].widget = forms.HiddenInput()
        self.fields['donation_note'].widget.attrs.update({'cols': 30, 'rows': 3, 'class': 'form-control'})
        self.fields['save_card'].widget.attrs.update({'class': 'm-2 form-check-input'})
        self.payment_errors = []

    def card_choices(self):
        if self.user is None:
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
            note = note + f", Donation of {self.cleaned_data['donation']}"
        logging.debug(self.cleaned_data)
        logging.debug(self.line_items)
        if self.cleaned_data['source_id'] == 'no-payment' and self.amount_initial == 0 \
                and self.cleaned_data['amount'] == 0:
            self.log = self.save(commit=False)
            self.log.user = self.user
            self.log.idempotency_key = idempotency_key
            self.log.checkout_created_time = timezone.now()
            self.log.total_money = 0
            self.log.receipt = 'None'
            self.log.description = note[:250]
            self.log.status = 'comped'
            self.log.save()
            return True
        payment_helper = PaymentHelper(self.user)
        logging.debug(idempotency_key)
        self.log = payment_helper.create_payment(
            amount=self.cleaned_data['amount'],
            category=self.cleaned_data['category'],
            donation=self.cleaned_data['donation'],
            idempotency_key=idempotency_key,
            note=note,
            source_id=self.cleaned_data['source_id'],
            saved_card_id=int(self.cleaned_data['card'])
        )

        if self.log is not None:
            pay_dict = {'line_items': self.line_items, 'total': self.cleaned_data['amount'],
                        'receipt': self.log.receipt}
            if self.user is not None:
                EmailMessage().payment_email_user(self.user, pay_dict)
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
        else:
            for error in payment_helper.errors:
                self.payment_errors.append(error)
                logging.debug(error)

        return False
