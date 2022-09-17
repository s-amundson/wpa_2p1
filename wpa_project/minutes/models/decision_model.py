import logging
from django.db import models
from django.utils import timezone
from .minutes_models import Minutes
logger = logging.getLogger(__name__)


class Decision(models.Model):
    decision_date = models.DateTimeField(default=timezone.now)
    minutes = models.ForeignKey(Minutes, on_delete=models.SET_NULL, null=True, default=None)
    text = models.TextField()
