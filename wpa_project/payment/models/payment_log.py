from django.conf import settings
from django.db import models

category_choices = [
    ('donation', 'Donation'),
    ('intro', 'Introductory Class'),
    ('joad', 'JOAD'),
    ('membership', 'Membership')]


class PaymentLog(models.Model):
    category = models.CharField(max_length=50, default='intro', choices=category_choices)
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
    volunteer_points = models.FloatField(default=0)
