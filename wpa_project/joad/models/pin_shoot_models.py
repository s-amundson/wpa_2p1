from django.db import models
from django.utils import timezone
from .joad_event_model import JoadEvent
from student_app.models import Student
from ..src import Choices

choices = Choices()


class CommonPin(models.Model):
    bow = models.CharField(max_length=45, choices=choices.bows())
    category = models.CharField(max_length=20, choices=choices.pin_shoot_catagory(), null=True, default=None)
    distance = models.IntegerField(choices=choices.distances(), null=True, default=None)
    target = models.IntegerField(choices=choices.targets(), null=True, default=None)
    inner_scoring = models.BooleanField(default=False)
    score = models.IntegerField(null=True, default=None)
    stars = models.IntegerField(choices.stars(), null=True, default=None)
# 'bow', 'category', 'distance', 'target', 'inner_scoring', 'score', 'stars'
    class Meta:
        abstract = True


class PinManager(models.Manager):
    def high_score(self, **kwargs):
        # the method accepts **kwargs, so that it is possible to filter
        return self.order_by('-score').first()


class PinScores(CommonPin):
    pass


class PinAttendance(CommonPin):
    event = models.ForeignKey(JoadEvent, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    attended = models.BooleanField(default=False)
    previous_stars = models.IntegerField(choices.stars(), default=0)
    pay_status = models.CharField(max_length=20, null=True, default=None)
    idempotency_key = models.CharField(max_length=40, null=True, default=None)
    award_received = models.BooleanField(default=False)

    objects = PinManager()
