
import logging
from django.db import models
from .student_family import StudentFamily

from django.utils import timezone
logger = logging.getLogger(__name__)


class Student(models.Model):
    student_family = models.ForeignKey(StudentFamily, on_delete=models.SET_NULL, null=True)

    # user fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()

    # # if this student_app has a record in the user table
    # login = models.BooleanField()

    # hidden fields
    safety_class = models.DateField(null=True)
