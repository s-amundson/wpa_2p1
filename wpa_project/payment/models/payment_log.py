from django.conf import settings
from django.db import models


class PaymentLog(models.Model):
    checkout_created_time = models.DateTimeField()
    description = models.CharField(max_length=255, null=True)
    donation = models.IntegerField(default=0)
    idempotency_key = models.UUIDField()
    location_id = models.CharField(max_length=100, null=True)
    order_id = models.CharField(max_length=100, null=True)
    payment_id = models.CharField(max_length=100, null=True)
    receipt = models.URLField(null=True)
    source_type = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=20, null=True)
    total_money = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
