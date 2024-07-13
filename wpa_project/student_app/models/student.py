import logging
from django.db import models
from django.conf import settings
from django.apps import apps

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
    signature = models.ImageField(upload_to="signatures/%Y/%m/%d/", null=True)
    signature_pdf = models.FileField(upload_to="signatures/%Y/%m/%d/", null=True)
    is_joad = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_user(self):
        User = apps.get_model('student_app', 'User')
        if self.user is None:
            # users = User.objects.none()
            return User.objects.filter(student__student_family=self.student_family)
            # family = self.student_family.student_set.filter(user__isnull=False)
            # logger.warning(family)
            # for s in family:
            #     # self.bcc_append_user(s.user)
            #     users = users | users.filter(id=s.user.id)
        else:
            users = User.objects.filter(id=self.user.id)
        return users
