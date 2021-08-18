from django.conf import settings
from django.contrib.auth.models import User
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


    # {'refund':
    #   {'amount_money': {'amount': 5, 'currency': 'USD'},
    #   'created_at': '2021-06-08T22:57:56.361Z',
    #   'id': 'hGlJwNfQxPQ5FjohtPrud7lKqpYZY_59WvXVSTGo3dcZKNNmkv5GMHeBcVuAPhKZiGmPsoNsM',
    #   'location_id': 'SVM1F73THA9W6',
    #   'order_id': '5NSwgFUNiBio3ksoL0iVgDFsCi4F',
    #   'payment_id': 'hGlJwNfQxPQ5FjohtPrud7lKqpYZY',
    #   'status': 'PENDING',
    #   'updated_at': '2021-06-08T22:57:56.361Z'}}