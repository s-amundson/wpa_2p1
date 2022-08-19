import logging

from django.dispatch import receiver, Signal
from .src import RefundHelper

payment_error_signal = Signal()
refund_helper_signal = Signal()


@receiver(refund_helper_signal)
def refund_helper(idempotency_key, amount, class_registration, **kwargs):
    r = RefundHelper().refund_with_idempotency_key(idempotency_key, amount)
    if r['status'] == 'SUCCESS':
        class_registration.pay_status = 'refunded'
        class_registration.save()
