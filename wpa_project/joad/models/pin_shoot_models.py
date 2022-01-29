from django.db import models
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

    class Meta:
        abstract = True


class PinScores(CommonPin):
    pass


class PinAttendance(CommonPin):
    event = models.ForeignKey(JoadEvent, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    attended = models.BooleanField(default=False)
    previous_stars = models.IntegerField(choices.stars(), default=0)
