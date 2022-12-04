from django.db import models
from django.conf import settings
from django.utils import timezone

from .session_model import Session
from event.models import Event
from src.model_helper import choices

import logging

logger = logging.getLogger(__name__)


class JoadClass(models.Model):
    class_states = ['scheduled', 'past', 'canceled']
    class_date = models.DateTimeField()
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=20, null=True, choices=choices(class_states), default='scheduled')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, default=None)

    def get_states(self):
        return self.class_states
