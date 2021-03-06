import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ClassRegistration
from payment.models import PaymentLog

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PaymentLog)
def registration_update(sender, instance, created, **kwargs):
    cr = ClassRegistration.objects.filter(idempotency_key=instance.idempotency_key)
    logging.debug(instance.status)
    if instance.status in ["SUCCESS", "COMPLETED"]:
        for c in cr:
            c.pay_status = 'paid'
            c.save()
