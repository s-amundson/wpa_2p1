from django.conf import settings
from django.db import models


class PaymentErrorLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    db_model = models.CharField(max_length=50, null=True)
    error_code = models.CharField(max_length=255, null=True)
    error_count = models.IntegerField(default=0)
    error_time = models.DateTimeField()
    idempotency_key = models.UUIDField()

