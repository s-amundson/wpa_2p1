import logging
from django.db import models
from . import Minutes
logger = logging.getLogger(__name__)

REPORT_CHOICES = ['President', 'Vice', 'Secretary', 'Treasure', 'Webmaster']


def make_choices(choice_list):
    choices = []
    for c in choice_list:
        choices.append((c.lower(), c))
    return choices


class Report(models.Model):
    minutes = models.ForeignKey(Minutes, on_delete=models.SET_NULL, null=True)
    owner = models.CharField(max_length=50, choices=make_choices(REPORT_CHOICES))
    report = models.TextField()

