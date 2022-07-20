from django.conf import settings
from django.db import models
from .customer import Customer


class Card(models.Model):
    bin = models.IntegerField(null=True, default=None)
    card_brand = models.CharField(max_length=20, null=True)
    card_type = models.CharField(max_length=20, null=True)
    card_id = models.CharField(max_length=50, null=True)
    cardholder_name = models.CharField(max_length=100, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    enabled = models.BooleanField()
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    fingerprint = models.CharField(max_length=100, null=True)
    last_4 = models.IntegerField()
    merchant_id = models.CharField(max_length=20, null=True)
    prepaid_type = models.CharField(max_length=20, null=True)
    version = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.card_brand} Ending in {self.last_4} Expires: {self.exp_month}/{self.exp_year}'
