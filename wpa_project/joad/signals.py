import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PinAttendance, Registration
from payment.models import PaymentLog
from payment.signals import payment_error_signal

logger = logging.getLogger(__name__)


@receiver(payment_error_signal)
def payment_error(old_idempotency_key, new_idempotency_key, **kwargs):
    """ in case of a payment error update the registration with the new idempotency key so that we register them once
    a successful payment is processed"""

    # event_reg = EventRegistration.objects.filter(idempotency_key=old_idempotency_key)
    # event_reg.update(idempotency_key=new_idempotency_key)

    pin_reg = PinAttendance.objects.filter(idempotency_key=old_idempotency_key)
    pin_reg.update(idempotency_key=new_idempotency_key)

    reg = Registration.objects.filter(idempotency_key=old_idempotency_key)
    reg.update(idempotency_key=new_idempotency_key)


@receiver(post_save, sender=PaymentLog)
def registration_update(sender, instance, created, **kwargs):
    if instance.status in ["SUCCESS", "COMPLETED"]:
        for cr in [Registration.objects.filter(idempotency_key=instance.idempotency_key),
                   # EventRegistration.objects.filter(idempotency_key=instance.idempotency_key),
                   PinAttendance.objects.filter(idempotency_key=instance.idempotency_key)]:
            for c in cr:
                c.pay_status = 'paid'
                c.save()
