import logging

from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from .models import ClassRegistration
from .src import ClassRegistrationHelper
from payment.models import PaymentLog
from payment.signals import payment_error_signal
from payment.src import RefundHelper

logger = logging.getLogger(__name__)


@receiver(payment_error_signal)
def registration_payment_error(old_idempotency_key, new_idempotency_key, **kwargs):
    """ in case of a payment error update the registration with the new idempotency key so that we register them once
    a successful payment is processed"""
    cr = ClassRegistration.objects.filter(idempotency_key=old_idempotency_key)
    cr.update(idempotency_key=new_idempotency_key)


@receiver(post_save, sender=PaymentLog)
def registration_update(sender, instance, created, **kwargs):
    crh = ClassRegistrationHelper()
    cr = ClassRegistration.objects.filter(idempotency_key=instance.idempotency_key)
    # logging.debug(instance.status)
    if instance.status in ["SUCCESS", "COMPLETED"]:
        for c in cr:
            c.pay_status = 'paid'
            c.save()
            crh.update_class_state(c.beginner_class)
