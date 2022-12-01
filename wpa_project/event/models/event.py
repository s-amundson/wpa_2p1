from django.db import models

from src.model_helper import choices

import logging
logger = logging.getLogger(__name__)


class Event(models.Model):
    event_states = ['scheduled', 'open', 'wait', 'full', 'closed', 'canceled', 'recorded']
    event_types = ['class', 'joad', 'special', 'work']
    # Fields
    event_date = models.DateTimeField()
    cost_standard = models.IntegerField(default=0)
    cost_member = models.IntegerField(default=0)

    state = models.CharField(max_length=20, null=True, choices=choices(event_states))
    type = models.CharField(max_length=20, null=True, choices=choices(event_types))
    volunteer_points = models.IntegerField(default=0)
