import logging
from django.db import models
from django.utils import timezone
logger = logging.getLogger(__name__)

REPORT_CHOICES = ['President', 'Vice', 'Secretary', 'Treasure']


def make_choices(choice_list):
    choices = []
    for c in choice_list:
        choices.append((c.lower(), c))
    return choices


class Minutes(models.Model):
    meeting_date = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=timezone.now)
    attending = models.CharField(max_length=250)
    minutes_text = models.CharField(max_length=250)
    memberships = models.IntegerField()
    balance = models.IntegerField(default=None, null=True)
    discussion = models.TextField()
    end_time = models.TimeField(null=True)


class MinutesReport(models.Model):
    minutes = models.ForeignKey(Minutes, on_delete=models.SET_NULL, null=True)
    owner = models.CharField(max_length=50, choices=make_choices(REPORT_CHOICES))
    report = models.TextField()


class MinutesBusiness(models.Model):
    minutes = models.ForeignKey(Minutes, on_delete=models.SET_NULL, null=True)
    added_date = models.DateField(default=timezone.now)
    business = models.TextField()
    resolved = models.DateField(default=None, null=True)


class MinutesBusinessUpdate(models.Model):
    business = models.ForeignKey(MinutesBusiness, on_delete=models.CASCADE)
    update_date = models.DateField(default=timezone.now)
    update_text = models.TextField()
