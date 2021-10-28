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

    # # if this student_app has a record in the user table
    # login = models.BooleanField()

    # hidden fields
    safety_class = models.DateField(null=True)
    covid_vax = models.BooleanField(default=False)
    # __original_email = None
    #
    # def __init__(self, *args, **kwargs):
    #     super(Student, self).__init__(*args, **kwargs)
    #     self.__original_email = self.email
    #
    # def save(self, force_insert=False, force_update=False, *args, **kwargs):
    #     if self.email != self.__original_email:
    #         #  send email to user
    #
    #     super(Student, self).save(force_insert, force_update, *args, **kwargs)
    #     self.__original_email = self.email