import logging
from django.db import models

logger = logging.getLogger(__name__)


class Level(models.Model):
    name = models.CharField(max_length=40)
    cost = models.IntegerField()
    description = models.TextField()
    enabled = models.BooleanField(default=False)
    min_age = models.IntegerField(default=None, null=True)
    max_age = models.IntegerField(default=None, null=True)
    is_family = models.BooleanField(default=False)
    additional_cost = models.IntegerField(default=None, null=True)
