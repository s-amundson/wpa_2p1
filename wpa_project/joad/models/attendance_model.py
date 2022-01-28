from django.db import models

from student_app.models import Student
from .joad_class import JoadClass

import logging
logger = logging.getLogger(__name__)


class Attendance(models.Model):
    joad_class = models.ForeignKey(JoadClass, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, limit_choices_to={'is_joad': True}, null=True)
    attended = models.BooleanField(default=False)
