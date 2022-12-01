import logging

from django.db import models
from src.model_helper import choices
from event.models import Event

logger = logging.getLogger(__name__)


class BeginnerCommonClass(models.Model):
    class_types = ['beginner', 'returnee', 'combined', 'special']
    class_states = ['scheduled', 'open', 'wait', 'full', 'closed', 'canceled', 'recorded']

    class_type = models.CharField(max_length=20, null=True, choices=choices(class_types))
    beginner_limit = models.IntegerField()
    beginner_wait_limit = models.IntegerField(default=0)
    returnee_limit = models.IntegerField()
    returnee_wait_limit = models.IntegerField(default=0)
    instructor_limit = models.IntegerField(default=10)
    state = models.CharField(max_length=20, null=True, choices=choices(class_states))
    cost = models.IntegerField(default=5)

    class Meta:
        abstract = True

    def get_states(self):
        return self.class_states


class BeginnerClass(BeginnerCommonClass):
    class_date = models.DateTimeField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, default=None)


class BeginnerSchedule(BeginnerCommonClass):
    class_time = models.TimeField()
    day_of_week = models.IntegerField(default=5) # Monday is 0 and Sunday is 6
    frequency = models.IntegerField(default=1)
    future_classes = models.IntegerField(default=6)
