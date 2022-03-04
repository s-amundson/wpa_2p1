from django.db import models
from .payment_log import PaymentLog


class DonationLog(models.Model):
    payment = models.ForeignKey(PaymentLog, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField(default=0)
    note = models.TextField()
