import logging
from django.db import models

logger = logging.getLogger(__name__)


class CostsModel(models.Model):
    name = models.CharField(max_length=40)
    member_cost = models.IntegerField()
    standard_cost = models.IntegerField()
    membership = models.BooleanField(default=False)
    enabled = models.BooleanField(default=False)
