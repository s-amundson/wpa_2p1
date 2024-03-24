from django import forms

from src.model_form import MyModelForm
from payment.models import PaymentErrorLog
from ..models import Registration
import logging

logger = logging.getLogger(__name__)


class CancelForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['donate'] = forms.BooleanField(
            widget=forms.CheckboxInput(attrs={'class': "m-2"}),
            required=False,
            initial=False,
            label='I wish to donate my refund')


class CancelSetForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = Registration
        required_fields = ['student']
        optional_fields = []
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].widget = forms.HiddenInput()

        cancel_attrs = {'class': "m-2 cancel-check"}
        if self.instance.pay_status in ['cancel_pending', 'refunded']:
            cancel_attrs['disabled'] = 'disabled'
        self.fields['cancel'] = forms.BooleanField(
            widget=forms.CheckboxInput(attrs=cancel_attrs),
            required=False,
            initial=False,
            label='Cancel')

        amount = 0
        # if self.instance.student.member_set.filter():

        if self.instance.pay_status == 'paid' and not (self.instance.student.user and self.instance.student.user.is_staff):
            amount = self.instance.event.cost_standard
            # TODO add member price if member when registered.
        self.pay_status = self.instance.pay_status
        if self.pay_status == 'start':
            self.pay_status = 'Unsuccessful'
        elif self.pay_status == 'wait error':
            payment_error = PaymentErrorLog.objects.filter(idempotency_key=self.instance.idempotency_key).last()
            self.pay_status = 'Error'
            if payment_error:
                self.pay_status += f": {payment_error.error_code.replace('_', ' ').title()}"

        self.fields['amount'] = forms.IntegerField(
            widget=forms.HiddenInput(attrs={'class': "cancel-amount"}),
            initial=amount,
            required=False
        )

        self.empty_permitted = False
