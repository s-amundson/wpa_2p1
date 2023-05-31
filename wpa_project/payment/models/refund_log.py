from django.db import models


class RefundLog(models.Model):
    amount = models.IntegerField()
    created_time = models.DateTimeField()
    location_id = models.CharField(max_length=50)
    order_id = models.CharField(max_length=192, null=True)
    payment_id = models.CharField(max_length=192, null=True)
    processing_fee = models.IntegerField(default=None, null=True)
    refund_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    volunteer_points = models.FloatField(default=0)
