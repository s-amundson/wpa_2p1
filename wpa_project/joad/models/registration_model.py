from django.db import models
from django.utils import timezone

from student_app.models import Student
from .session_model import Session

import logging
logger = logging.getLogger(__name__)


class Registration(models.Model):
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, limit_choices_to={'is_joad': True}, null=True)
    pay_status = models.CharField(max_length=20)
    idempotency_key = models.UUIDField()
    reg_time = models.DateField(default=timezone.now)
