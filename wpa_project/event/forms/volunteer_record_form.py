from django import forms
from django.utils import timezone

from src.model_form import MyModelForm
from ..models import Event, VolunteerRecord
import logging

logger = logging.getLogger(__name__)


class VolunteerRecordForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = VolunteerRecord
        required_fields = ['student', 'volunteer_points']
        optional_fields = ['event']
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        self.student_family = None
        self.student = None
        if 'student' in kwargs:
            self.student = kwargs.pop('student')
        if 'student_family' in kwargs:
            self.student_family = kwargs.pop('student_family')
        super().__init__(*args, **kwargs)
        self.fields['event'].label += ' (Optional)'
        self.fields['volunteer_points'].label += ': Enter volunteer points to add (Negative value subtracts)'
        if self.student:
            self.student_family = self.student.student_family
            self.fields['student'].queryset = self.fields['student'].queryset.filter(student_family=self.student_family)
            self.fields['student'].initial = self.student
        elif self.student_family:
            self.fields['student'].queryset = self.fields['student'].queryset.filter(student_family=self.student_family)

