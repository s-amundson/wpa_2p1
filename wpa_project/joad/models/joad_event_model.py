from django.db import models
from django.utils import timezone

from ..src import Choices
from event.models import Event

import logging
logger = logging.getLogger(__name__)

choices = Choices()


class JoadEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, default=None)
    c = choices.event_types()
    event_type = models.CharField(max_length=40, null=True, choices=c, default=c[0])
    student_limit = models.IntegerField(default=24)
    pin_cost = models.IntegerField(null=True, default=None)

    def __str__(self):
        if self.event:
            d = timezone.localtime(self.event.event_date).strftime("%d %b, %Y %I:%M %p")
            return f'{d} Cost: ${self.event.cost_standard} Pin Cost: ${self.pin_cost}'
        else:
            return super().__str__()
