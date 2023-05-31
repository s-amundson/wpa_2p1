from django.db import models

from .session_model import Session
from event.models import Event

import logging

logger = logging.getLogger(__name__)


class JoadClass(models.Model):
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, default=None)

    # def get_states(self):
    #     return self.class_states
