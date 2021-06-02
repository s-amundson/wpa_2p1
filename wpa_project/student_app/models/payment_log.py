from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class PaymentLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    student_family = models.ForeignKey('student_app.StudentFamily', on_delete=models.SET_NULL, null=True)
    checkout_created_time = models.DateTimeField()
    checkout_id = models.CharField(max_length=50, null=True)
    order_id = models.CharField(max_length=50, null=True)
    location_id = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=20, null=True)
    total_money = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=50, null=True)
    idempotency_key = models.UUIDField()
    receipt = models.CharField(max_length=100, null=True)

