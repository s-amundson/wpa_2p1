
import logging
import uuid

from django.db import models
from .beginner_class import BeginnerClass
from .student import Student

from django.utils import timezone
logger = logging.getLogger(__name__)


class ClassRegistration(models.Model):
    beginner_class = models.ForeignKey(BeginnerClass, on_delete=models.SET_NULL, null=True)
    student_family = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    number_students = models.IntegerField()
    pay_status = models.CharField(max_length=20)
    idempotency_key = models.UUIDField(default=str(uuid.uuid4()))
