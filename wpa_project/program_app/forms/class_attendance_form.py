from django import forms

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
            if cr.new_student:
                self.new_students.append({'id': cr.student.id, 'first_name': cr.student.first_name,
                                          'last_name': cr.student.last_name, 'dob': cr.student.dob,
                                          'check': f'check_{cr.student.id}', 'checked': cr.attended, 'cr_id': cr.id,
                                          'signature': (cr.signature is not None)})
            else:
                self.return_students.append({'id': cr.student.id, 'first_name': cr.student.first_name,
                                             'last_name': cr.student.last_name, 'dob': cr.student.dob,
                                             'check': f'check_{cr.student.id}', 'checked': cr.attended, 'cr_id': cr.id,
                                             'signature': (cr.signature is not None)})
