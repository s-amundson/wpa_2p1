from django.db import models
from django.conf import settings
from django.utils import timezone

from ..src import Choices
import logging
logger = logging.getLogger(__name__)

choices = Choices()


class JoadEvent(models.Model):
    cost = models.IntegerField(default=15)
    event_date = models.DateTimeField(default=None, null=True)
    c = choices.event_types()
    event_type = models.CharField(max_length=40, null=True, choices=c, default=c[0])
    state = models.CharField(max_length=20, null=True, choices=choices.class_states(), default='open')
    student_limit = models.IntegerField(default=24)

    def __str__(self):
        return timezone.localtime(self.event_date).strftime("%d %b, %Y %I:%M %p")
