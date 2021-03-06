from django.apps import apps
from django.db import models
from .beginner_class import BeginnerClass

import logging
logger = logging.getLogger(__name__)


class ClassRegistration(models.Model):
    beginner_class = models.ForeignKey(BeginnerClass, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(apps.get_model('student_app', 'Student', require_ready=False),
                                on_delete=models.SET_NULL, null=True)
    new_student = models.BooleanField()
    pay_status = models.CharField(max_length=20)
    idempotency_key = models.UUIDField()
    reg_time = models.DateTimeField(auto_now_add=True, blank=True)
    attended = models.BooleanField(default=False)


class ClassRegistrationAdmin(models.Model):
    class_registration = models.ForeignKey(ClassRegistration, on_delete=models.SET_NULL, null=True)
    staff = models.ForeignKey(apps.get_model('student_app', 'User', require_ready=False),
                                on_delete=models.SET_NULL, null=True)
    note = models.TextField()
