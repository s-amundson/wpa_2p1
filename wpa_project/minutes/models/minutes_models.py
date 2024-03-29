import logging
from django.db import models
from django.utils import timezone
logger = logging.getLogger(__name__)


class Minutes(models.Model):
    meeting_date = models.DateTimeField(default=timezone.now)
    attending = models.CharField(max_length=250)
    minutes_text = models.CharField(max_length=250)
    memberships = models.IntegerField()
    balance = models.FloatField(default=None, null=True)
    discussion = models.TextField()
    end_time = models.DateTimeField(null=True)
    reimbursement_review = models.BooleanField(default=False)

    def __str__(self):
        return f'Minutes: {self.meeting_date.date()}'
