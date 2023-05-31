import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Registration
from payment.models import PaymentLog
from payment.signals import payment_error_signal
from program_app.src import ClassRegistrationHelper

logger = logging.getLogger(__name__)


@receiver(payment_error_signal)
def payment_error(old_idempotency_key, new_idempotency_key, **kwargs):
    """ in case of a payment error update the registration with the new idempotency key so that we register them once
    a successful payment is processed"""

    reg = Registration.objects.filter(idempotency_key=old_idempotency_key)
    reg.update(idempotency_key=new_idempotency_key)


@receiver(post_save, sender=PaymentLog)
def registration_update(sender, instance, created, **kwargs):
    # crh = ClassRegistrationHelper()
    cr = Registration.objects.filter(idempotency_key=instance.idempotency_key)
    is_intro_class = False
    if instance.status in ["SUCCESS", "COMPLETED", 'volunteer points']:
        for c in cr:
            c.pay_status = 'paid'
            c.save()
            if c.event.beginnerclass_set.last():
                is_intro_class = True
        if is_intro_class:
            ClassRegistrationHelper().update_class_state(cr[0].event.beginnerclass_set.last())