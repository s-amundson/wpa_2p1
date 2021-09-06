import logging
from django.db import models
from django.utils import timezone
from django.apps import apps
from .minutes_models import Minutes
logger = logging.getLogger(__name__)


class Business(models.Model):
    minutes = models.ForeignKey(Minutes, on_delete=models.SET_NULL,
                                null=True)
    added_date = models.DateField(default=timezone.now)
    business = models.TextField()
    resolved = models.DateField(default=None, null=True)


class BusinessUpdate(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    update_date = models.DateField(default=timezone.now)
    update_text = models.TextField()
