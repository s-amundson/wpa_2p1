
import logging
import uuid

from django.db import models
from .student import Student
from django.utils import timezone
logger = logging.getLogger(__name__)


class BeginnerClass(models.Model):
    class_date = models.DateField()
    enrolled_beginners = models.IntegerField(default=0)
    beginner_limit = models.IntegerField()
    enrolled_returnee = models.IntegerField(default=0)
    returnee_limit = models.IntegerField()
