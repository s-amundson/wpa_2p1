from django import forms

from event.models import Registration
from payment.models import PaymentErrorLog
import logging

logger = logging.getLogger(__name__)


class AdmitWaitForm(forms.ModelForm):
    # this is used in formsets.
    admit = forms.BooleanField(required=False)

    class Meta:
        model = Registration
        required_fields = ['student']
        optional_fields = ['admit']
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pay_status = 'waiting'
        self.fields['student'].disabled = True
        if self.instance.id:
            if self.instance.pay_status != 'waiting':
                self.fields['admit'].disabled = True
                if self.instance.pay_status.startswith('wait '):
                    self.pay_status = self.instance.pay_status[5:].title()
                if self.instance.pay_status == 'wait error':
                    payment_error = PaymentErrorLog.objects.filter(idempotency_key=self.instance.idempotency_key).last()
                    if payment_error:
                        self.pay_status += f": {payment_error.error_code.replace('_', ' ').title()}"
