import logging

from django.db import models
logger = logging.getLogger(__name__)


def choices(choice_list):
    choice = []
    for c in choice_list:
        choice.append((c, c))
    return choice


class BeginnerClass(models.Model):
    class_types = ['beginner', 'returnee', 'combined']
    class_states = ['scheduled', 'open', 'full', 'closed', 'canceled', 'recorded']

    class_date = models.DateTimeField()
    class_type = models.CharField(max_length=20, null=True, choices=choices(class_types))
    beginner_limit = models.IntegerField()
    returnee_limit = models.IntegerField()
    instructor_limit = models.IntegerField(default=10)
    state = models.CharField(max_length=20, null=True, choices=choices(class_states))
    cost = models.IntegerField(default=5)

    def get_states(self):
        return self.class_states
