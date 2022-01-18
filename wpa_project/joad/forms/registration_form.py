from datetime import timedelta
from django import forms
from django.utils import timezone
from django.db.models import Q
from src.model_form import MyModelForm
from student_app.models import Student
from ..models import Registration, Session
import uuid
import logging

logger = logging.getLogger(__name__)


class RegistrationForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Registration
        required_fields = ['session']
        optional_fields = []
        fields = optional_fields + required_fields

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_board:
            students = Student.objects.filter(is_joad=True)
        else:
            students = Student.objects.get(user=user).student_family.student_set.filter(is_joad=True)
        d = timezone.localdate(timezone.now())
        d = d.replace(year=d.year - 20)
        students = students.filter(dob__gt=d).order_by('last_name')
        for student in students:
            self.fields[f'student_{student.id}'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check"}), required=False,
                label=f'{student.first_name} {student.last_name}', initial=True)
        self.fields['session'].queryset = Session.objects.filter(state='open').order_by('start_date')

    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('student_'):
                yield self[field_name]

    def save(self, commit=True):
        logging.debug('save')
