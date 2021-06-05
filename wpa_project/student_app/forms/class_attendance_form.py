from django import forms
from django.forms import TextInput, ModelForm
from django.utils import timezone

from ..models import BeginnerClass, ClassRegistration
import logging

logger = logging.getLogger(__name__)


class ClassAttendanceForm(forms.Form):

    def __init__(self, beginner_class, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_closed = beginner_class.state == 'closed'
        self.new_students = []
        self.return_students = []
        self.class_registration = beginner_class.classregistration_set.all()
        for cr in self.class_registration:
            student = cr.student
            if cr.new_student:
                self.new_students.append({'id': cr.student.id, 'first_name': cr.student.first_name,
                                          'last_name': cr.student.last_name, 'dob': cr.student.dob,
                                          'check': f'check_{cr.student.id}', 'checked': cr.attended})
            else:
                self.return_students.append({'id': student.id, 'first_name': student.first_name,
                                             'last_name': student.last_name, 'dob': student.dob,
                                             'check': f'check_{student.id}', 'checked': cr.attended})
