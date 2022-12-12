from django.apps import apps
from django.db import models
from django.utils import timezone

from student_app.models import User
from event.models import Event
from src.model_helper import choices
import logging
logger = logging.getLogger(__name__)

class RegistrationManager(models.Manager):
    def get_queryset(self):
        return RegistrationQuerySet(self.model, using=self._db)

    def attendance(self):
        return self.get_queryset().attendance()


class RegistrationQuerySet(models.QuerySet):
    def attendance(self):
        return self.filter(
            beginner_class__event__event_date__lt=timezone.now(),
            pay_status__in=['paid', 'admin']
        ).aggregate(
            attended=models.Count('id', filter=models.Q(attended=True)),
            registrations=models.Count('id', distinct=True)
        )

    def attended_count(self):
        return self.attendance()['attended']

    def beginner_count(self, date):
        qs = self.filter(pay_status__in=['paid', 'admin'])
        qs = qs.filter(models.Q(student__safety_class__isnull=True) | models.Q(student__safety_class__gte=date))
        qs = qs.filter(models.Q(student__user__is_staff=False) | models.Q(student__user__isnull=True))
        return qs.count()

    def returnee_count(self, date):
        qs = self.filter(pay_status__in=['paid', 'admin'], student__safety_class__isnull=False)
        qs = qs.filter(models.Q(student__user__is_staff=False) | models.Q(student__user__isnull=True))
        return qs.filter(student__safety_class__lt=date).count()

    def staff_count(self):
        return self.filter(student__user__is_staff=True, pay_status__in=['paid', 'admin']).count()

class Registration(models.Model):
    pay_statuses = ['admin', 'canceled', 'paid', 'refund', 'refund donated', 'refunded', 'start']
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, default=None)
    student = models.ForeignKey(apps.get_model('student_app', 'Student', require_ready=False),
                                on_delete=models.SET_NULL, null=True)
    pay_status = models.CharField(max_length=20, choices=choices(pay_statuses))
    idempotency_key = models.UUIDField()
    reg_time = models.DateTimeField(auto_now_add=True, blank=True)
    attended = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    objects = RegistrationManager()


class RegistrationAdmin(models.Model):
    class_registration = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True)
    staff = models.ForeignKey(apps.get_model('student_app', 'User', require_ready=False),
                                on_delete=models.SET_NULL, null=True)
    note = models.TextField()
