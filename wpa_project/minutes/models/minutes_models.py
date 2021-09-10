import logging
from django.db import models
from django.utils import timezone
logger = logging.getLogger(__name__)


class Minutes(models.Model):
    meeting_date = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=timezone.now)
    attending = models.CharField(max_length=250)
    minutes_text = models.CharField(max_length=250)
    memberships = models.IntegerField()
    balance = models.IntegerField(default=None, null=True)
    discussion = models.TextField()
    end_time = models.TimeField(null=True)
