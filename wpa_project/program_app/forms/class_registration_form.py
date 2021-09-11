from datetime import timedelta
from django import forms
from django.utils import timezone
from ..models import BeginnerClass, ClassRegistration
import logging

logger = logging.getLogger(__name__)


class ClassRegistrationForm(forms.Form):

    def __init__(self, students, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bc = self.get_open_classes()
        self.fields['beginner_class'] = forms.ChoiceField(choices=bc)
        self.fields['terms'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2"}), required=True, label=f'I agree to the terms of the AWRL',
                initial=False)
        self.students = list(students.values())

        for student in students:
            self.fields[f'student_{student.id}'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check", 'is_beginner': 'T' if student.safety_class is None else 'F',
                       'dob': f"{student.dob}"}), required=False,
                label=f'{student.first_name} {student.last_name}', initial=True)
            # TODO WISH set initial to student's last class state
            # student['checkbox'] = self.fields[f'student_{student["id"]}']

    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('student_'):
                yield self[field_name]

    def get_open_classes(self):
        classes = BeginnerClass.objects.filter(class_date__gt=timezone.now(), state__exact='open')
        d = [("", "None")]
        for c in classes:
            cd = timezone.localtime(c.class_date)
            s = cd.strftime("%d %b, %Y %I:%M %p")
            d.append((str(c.id), s))
        return d

    class Meta:
        model = ClassRegistration
        exclude = ['pay_status', 'order_id', 'reg_time']
