from django.db import models
from django.conf import settings
from django.utils import timezone

from .session_model import Session

import logging

logger = logging.getLogger(__name__)


def choices(choice_list):
    choice = []
    for c in choice_list:
        choice.append((c, c))
    return choice


class JoadClass(models.Model):
    class_states = ['scheduled', 'past', 'canceled']
    class_date = models.DateTimeField()
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=20, null=True, choices=choices(class_states), default='scheduled')

    # def __str__(self):
    #     return f'{self.start_date}'

    def get_states(self):
        return self.class_states
