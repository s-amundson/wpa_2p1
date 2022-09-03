import logging

from django.db import models
logger = logging.getLogger(__name__)


def choices(choice_list):
    choice = []
    for c in choice_list:
        choice.append((c, c))
    return choice


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


class BeginnerSchedule(BeginnerCommonClass):
    class_time = models.TimeField()
    day_of_week = models.IntegerField(default=5) # Monday is 0 and Sunday is 6
    frequency = models.IntegerField(default=1)
    future_classes = models.IntegerField(default=6)
