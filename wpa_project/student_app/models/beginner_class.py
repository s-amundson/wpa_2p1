import logging

from django.db import models
from django.apps import apps
from django.utils import timezone
logger = logging.getLogger(__name__)


class BeginnerClass(models.Model):
    class_states = ['scheduled', 'open', 'full', 'closed', 'canceled', 'recorded']
    states = []
    for c in class_states:
        states.append((c, c))
    class_date = models.DateField()
    enrolled_beginners = models.IntegerField(default=0)
    beginner_limit = models.IntegerField()
    enrolled_returnee = models.IntegerField(default=0)
    returnee_limit = models.IntegerField()
    # states = [('scheduled', 'scheduled'), ('open', 'open'), ('full', 'full'), ('closed', 'closed'),
    #           ('canceled', 'canceled'), ('recorded', 'recorded')]
    state = models.CharField(max_length=20, null=True, choices=states)
    cost = models.IntegerField(default=5)


    def get_states(self):
        return self.class_states
    # def get_open_classes(self):
    #     classes = self.objects.filter(class_date__gt=timezone.now(), state__exact='open')
    #     d = [("", "None")]
    #     for c in classes:
    #         d.append((str(c.class_date), str(c.class_date)))
    #     return d
