from django import forms
from django.forms import TextInput, ModelForm
from django.utils import timezone

from ..models import BeginnerClass, ClassRegistration
import logging

logger = logging.getLogger(__name__)


class ClassRegistrationForm(forms.Form):

    def __init__(self, students, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bc = self.get_open_classes()
        self.fields['beginner_class'] = forms.ChoiceField(choices=bc)
        self.students = list(students.values())
        # logging.debug(self.students)
        # for student in self.students:
        #     student['box'] = forms.BooleanField(
        #         widget=forms.CheckboxInput(attrs={'class': "m-2"}), required=False,)
        for student in students:
            logging.debug(student)
            self.fields[f'student_{student.id}'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2"}), required=False, label=f'{student.first_name} {student.last_name}',
                initial=True)
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
            d.append((str(c.class_date), str(c.class_date)))
        return d


    class Meta:
        model = ClassRegistration
        exclude = ['pay_status', 'idempotency_key', 'reg_time']
