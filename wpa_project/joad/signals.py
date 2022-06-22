import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EventRegistration, PinAttendance, Registration
from payment.models import PaymentLog

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PaymentLog)
def registration_update(sender, instance, created, **kwargs):
    if instance.status in ["SUCCESS", "COMPLETED"]:
        for cr in [Registration.objects.filter(idempotency_key=instance.idempotency_key),
                   EventRegistration.objects.filter(idempotency_key=instance.idempotency_key),
                   PinAttendance.objects.filter(idempotency_key=instance.idempotency_key)]:
            for c in cr:
                c.pay_status = 'paid'
                c.save()

