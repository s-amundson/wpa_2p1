from datetime import timedelta
from django import forms
from django.utils import timezone
from django.db.models import Q
from ..models import BeginnerClass, ClassRegistration
import logging

logger = logging.getLogger(__name__)


class ClassRegistrationForm(forms.Form):

    def __init__(self, students, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bc = self.get_open_classes(user)
        self.fields['beginner_class'] = forms.ChoiceField(choices=bc)
        self.fields['terms'] = forms.BooleanField(
            widget=forms.CheckboxInput(attrs={'class': "m-2"}), required=True,
            label=f'I agree to the terms of the AWRL, COVID-19 Policy and the Cancellation Policy',
            initial=False)
        self.students = list(students.values())

        for student in students:
            self.fields[f'student_{student.id}'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check", 'is_beginner': 'T' if student.safety_class is None else 'F',
                       'dob': f"{student.dob}"}), required=False,
                label=f'{student.first_name} {student.last_name}', initial=True)

    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('student_'):
                yield self[field_name]

    def get_open_classes(self, user):
        classes = BeginnerClass.objects.filter(class_date__gt=timezone.now())
        if user.is_staff:
            classes = classes.filter(Q(state='open') | Q(state='full'))
        else:
            classes = classes.filter(state='open')
        d = [("", "None")]
        for c in classes:
            cd = timezone.localtime(c.class_date)
            s = cd.strftime("%d %b, %Y %I:%M %p")
            d.append((str(c.id), s))
        return d

    class Meta:
        model = ClassRegistration
        exclude = ['pay_status', 'order_id', 'reg_time']
