from django import forms
from django.forms import TextInput, ModelForm
from django.utils import timezone

from ..models import BeginnerClass, ClassRegistration
import logging

logger = logging.getLogger(__name__)


class ClassAttendanceForm(forms.Form):

    def __init__(self, beginner_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # bc = self.get_open_classes()
        # self.fields['beginner_class'] = forms.ChoiceField(choices=bc)
        self.is_closed = beginner_class.state == 'closed'
        self.new_students = []
        self.return_students = []
        self.class_registration = beginner_class.classregistration_set.all()
        for cr in self.class_registration:
            student = cr.student
            # w = forms.CheckboxInput(attrs={'class': "m-2", 'name': f'check_{student.id}'})
            if cr.new_student:
                self.new_students.append({'id': cr.student.id, 'first_name': cr.student.first_name,
                                          'last_name': cr.student.last_name, 'dob': cr.student.dob,
                                          'check': f'check_{cr.student.id}', 'checked': cr.attended})
            else:
                self.return_students.append({'id': student.id, 'first_name': student.first_name,
                                             'last_name': student.last_name, 'dob': student.dob,
                                             'check': f'check_{student.id}', 'checked': cr.attended})
            logging.debug(student.id)
            logging.debug(cr.attended)
            # self.fields[f'student_{student.id}'] = forms.BooleanField(widget=forms.CheckboxInput(
            #     attrs={'class': "m-2"}), required=False, label=f'{student.first_name} {student.last_name}',
            #     initial=False, disabled=beginner_class.state != 'closed')

    # def get_boxes(self):
    #     for field_name in self.fields:
    #         if field_name.startswith('student_'):
    #             yield self[field_name]
    #
    # def get_open_classes(self):
    #     classes = BeginnerClass.objects.filter(class_date__gt=timezone.now(), state__exact='open')
    #     d = [("", "None")]
    #     for c in classes:
    #         d.append((str(c.class_date), str(c.class_date)))
    #     return d

    #
    # class Meta:
    #     model = ClassRegistration
    #     exclude = ['pay_status', 'idempotency_key', 'reg_time']
