from django import forms
from django.utils import timezone

from ..models import Card, Customer, PaymentLog
from ..src import CardHelper, CustomerHelper, EmailMessage, PaymentHelper
from event.models import VolunteerRecord

import logging
logger = logging.getLogger(__name__)


class PaymentForm(forms.ModelForm):
    amount = forms.IntegerField(required=True)
    card = forms.ChoiceField(required=True)
    donation_note = forms.CharField(widget=forms.Textarea, required=False)
    default_card = forms.BooleanField(required=False, initial=False, label='Set card as default')
    save_card = forms.BooleanField(required=False, initial=False, label='Save card for future purchases')
    source_id = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = PaymentLog
        fields = ('amount', 'card', 'category', 'default_card', 'donation', 'donation_note', 'save_card', 'source_id',
                  'volunteer_points')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        # logging.debug(user)
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
        self.available_volunteer_points = 0
        if self.user and self.user.student_set.last() and self.user.student_set.last().student_family:
            self.available_volunteer_points = VolunteerRecord.objects.get_family_points(
                self.user.student_set.last().student_family)
        self.fields['volunteer_points'] = forms.FloatField(max_value=self.available_volunteer_points, required=False)
        self.fields['card'].choices = self.card_choices()
        self.fields['category'].widget = forms.HiddenInput()
        self.fields['donation_note'].widget.attrs.update({'cols': 30, 'rows': 3, 'class': 'form-control'})
        self.fields['save_card'].widget.attrs.update({'class': 'm-2 form-check-input'})
        if len(self.fields['card'].choices) > 1:
            self.fields['default_card'].widget.attrs.update({'class': 'm-2 form-check-input'})
        else:
            self.fields['default_card'].widget.attrs.update({'class': 'm-2 form-check-input', 'disabled': 'disabled'})
            self.fields['default_card'].initial = True
        self.payment_errors = []

    def card_choices(self):
        if self.user is None:
            return [(0, "New Card")]
        saved_cards = Card.objects.filter(customer__user=self.user, enabled=True).order_by('-default')
        card_choices = []
        for card in saved_cards:
            card_choices.append((card.id, str(card)))
        card_choices.append((0, "New Card"))
        return card_choices

    def process_payment(self, idempotency_key):
        note = self.description
        if self.cleaned_data['donation'] > 0:
            note = note + f", Donation of {self.cleaned_data['donation']}"
        volunteer_points = self.cleaned_data.get('volunteer_points', 0)
        if volunteer_points is None:
            volunteer_points = 0

        if self.cleaned_data['source_id'] == 'no-payment' and self.amount_initial == 0 \
                and self.cleaned_data['amount'] == 0:
            self.save_log(idempotency_key, note, 'comped', volunteer_points)
            return True
        if self.available_volunteer_points >= self.amount_initial and \
                volunteer_points >= self.amount_initial + self.cleaned_data['donation']:
            self.save_log(idempotency_key, note, 'volunteer_points', volunteer_points)
            duplicate = False
            # return True
        else:
            payment_helper = PaymentHelper(self.user)
            self.log, duplicate = payment_helper.create_payment(
                amount=self.cleaned_data['amount'] - volunteer_points,
                category=self.cleaned_data['category'],
                donation=self.cleaned_data['donation'],
                idempotency_key=idempotency_key,
                note=note,
                source_id=self.cleaned_data['source_id'],
                saved_card_id=int(self.cleaned_data['card'])
            )

        if self.log is not None:
            pay_dict = {'line_items': self.line_items, 'total': self.cleaned_data['amount'] + volunteer_points,
                        'receipt': self.log.receipt}
            if self.user is not None and not duplicate:
                EmailMessage().payment_email_user(self.user, pay_dict)
            if volunteer_points:
                vr = VolunteerRecord.objects.create(
                    student=self.user.student_set.last(),
                    volunteer_points= 0 - volunteer_points
                )
            if self.cleaned_data['save_card']:
                customer = Customer.objects.filter(user=self.user).last()
                # logging.debug(customer)
                if customer is None:
                    ch = CustomerHelper(self.user)
                    customer = ch.create_customer()
                if customer is not None:
                    card_helper = CardHelper()
                    card = card_helper.create_card_from_payment(customer, self.log, self.cleaned_data['default_card'])
                    return card is not None
            return True
        else:
            for error in payment_helper.errors:
                self.payment_errors.append(error)
                logging.warning(error)
        return False

    def save_log(self, idempotency_key, note, status, volunteer_points=0):
        logging.warning('save_log')
        self.log = self.save(commit=False)
        self.log.user = self.user
        self.log.idempotency_key = idempotency_key
        self.log.checkout_created_time = timezone.now()
        self.log.total_money = 0
        self.log.receipt = 'None'
        self.log.description = note[:250]
        self.log.status = status
        self.log.volunteer_points = volunteer_points
        self.log.save()