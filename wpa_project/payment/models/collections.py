from django.conf import settings
from django.db import models
from django.utils import timezone
from student_app.models import Student
import logging
logger = logging.getLogger(__name__)


class Collections(models.Model):
    cash = models.IntegerField(default=0)
    collected_date = models.DateTimeField(default=timezone.datetime.now)
    treasurer = models.ForeignKey(Student, on_delete=models.DO_NOTHING, null=True, related_name="+")
    board_member = models.ForeignKey(Student, on_delete=models.DO_NOTHING, null=True, related_name="+")
    note = models.CharField(max_length=200, default=None, null=True)
