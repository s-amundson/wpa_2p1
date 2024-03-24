from django.db import models

from .event import Event
from student_app.models import Student

import logging
logger = logging.getLogger(__name__)


class VolunteerAward(models.Model):
    events = models.ManyToManyField(Event)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, default=None)
    received = models.BooleanField(default=False)
    award = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    award_date = models.DateTimeField(auto_now=True)

class VolunteerEventManager(models.Manager):
    def get_queryset(self):
        return VolunteerEventQueryset(self.model, using=self._db)

    # def registered_count(self):
    #     return self.get_queryset().registered_count()


class VolunteerEventQueryset(models.QuerySet):
    def registered_count(self):
        count = self.filter(canceled=False).count()
        logger.warning(count)
        return count


class VolunteerEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, default=None)
    volunteer_limit = models.IntegerField(default=20)
    description = models.TextField()

    objects = VolunteerEventManager()


class VolunteerRecordManager(models.Manager):
    def get_family_points(self, family):
        vr = self.get_queryset().filter(student__in=family.student_set.all())
        if vr:
            return vr.aggregate(models.Sum('volunteer_points'))['volunteer_points__sum']
        return 0

    def update_points(self, event, student, points):
        if points:
            record, created = self.get_or_create(event=event, student=student, defaults={'volunteer_points': points})
            if not created:
                record.volunteer_points = points
                record.save()
        else:
            try:
                record = self.get(event=event, student=student)
                record.volunteer_points = points
                record.save()
            except self.model.DoesNotExist:
                return None
        return record


class VolunteerRecord(models.Model):
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, default=None)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    volunteer_points = models.FloatField(default=0)

    objects = VolunteerRecordManager()
