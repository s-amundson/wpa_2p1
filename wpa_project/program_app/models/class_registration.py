import logging

from django.apps import apps
from django.db import models
from .beginner_class import BeginnerClass


from django.utils import timezone
logger = logging.getLogger(__name__)


class ClassRegistration(models.Model):
    beginner_class = models.ForeignKey(BeginnerClass, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(apps.get_model('student_app', 'Student', require_ready=False),
                                on_delete=models.SET_NULL, null=True)
    new_student = models.BooleanField()
    pay_status = models.CharField(max_length=20)
    idempotency_key = models.UUIDField()
    reg_time = models.DateField(default=timezone.now)
    attended = models.BooleanField(default=False)
    signature = models.ImageField(upload_to="signatures/%Y/%m/%d/", null=True )
