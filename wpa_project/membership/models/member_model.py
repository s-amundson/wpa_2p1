import logging
from django.db import models
from django.utils import timezone

from student_app.models import Student
from .level_model import LevelModel
logger = logging.getLogger(__name__)


class MemberModel(models.Model):
    # user fields
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    expire_date = models.DateField(default=timezone.now)
    level = models.ForeignKey(LevelModel, on_delete=models.SET_NULL, null=True)

    # hidden fields
    join_date = models.DateField(default=timezone.now)

