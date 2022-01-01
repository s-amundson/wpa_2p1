import logging
from django.db import models
from django.conf import settings

from .student_family import StudentFamily

from django.utils import timezone
logger = logging.getLogger(__name__)


class Student(models.Model):
    student_family = models.ForeignKey(StudentFamily, on_delete=models.SET_NULL, null=True, default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, default=None)

    # user fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    email = models.EmailField(null=True, default=None, unique=True)

    # hidden fields
    safety_class = models.DateField(null=True)
    covid_vax = models.BooleanField(default=False)
