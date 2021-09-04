import logging
from django.db import models
from django.utils import timezone

from .level_model import Level
logger = logging.getLogger(__name__)


class Membership(models.Model):
    """ Log of membership entries """
    students = models.ManyToManyField('student_app.Student')
    effective_date = models.DateField(default=timezone.now)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    pay_status = models.CharField(max_length=20)
    idempotency_key = models.UUIDField()

