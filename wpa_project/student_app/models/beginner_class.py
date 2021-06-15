import logging

from django.db import models
logger = logging.getLogger(__name__)


class BeginnerClass(models.Model):
    class_states = ['scheduled', 'open', 'full', 'closed', 'canceled', 'recorded']
    states = []
    for c in class_states:
        states.append((c, c))
    class_date = models.DateField()
    beginner_limit = models.IntegerField()
    returnee_limit = models.IntegerField()
    state = models.CharField(max_length=20, null=True, choices=states)
    cost = models.IntegerField(default=5)

    def get_states(self):
        return self.class_states
