from django.db import models

from src.model_helper import choices

import logging
logger = logging.getLogger(__name__)


class Session(models.Model):
    class_states = ['scheduled', 'open', 'full', 'closed', 'canceled', 'recorded']

    cost = models.IntegerField(default=120)
    start_date = models.DateField(default=None, null=True)
    state = models.CharField(max_length=20, null=True, choices=choices(class_states))
    student_limit = models.IntegerField()

    def __str__(self):
        return f'{self.start_date}'

    def get_states(self):
        return self.class_states
