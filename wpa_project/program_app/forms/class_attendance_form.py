from django import forms
from ..src.class_registration_helper import ClassRegistrationHelper
import logging

logger = logging.getLogger(__name__)


class ClassAttendanceForm(forms.Form):

    def __init__(self, beginner_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crh = ClassRegistrationHelper()
        self.is_closed = beginner_class.state == 'closed'
        self.new_students = []
        self.return_students = []
        self.instructors = []
        self.class_registration = beginner_class.classregistration_set.all()
        self.class_date = beginner_class.class_date

        for cr in self.class_registration:
            if cr.new_student:
                self.new_students.append(self.student_dict(cr, bool(cr.signature)))
            else:
                try:
                    is_instructor = cr.student.user.is_instructor
                except (cr.student.DoesNotExist, AttributeError):
                    is_instructor = False
                if is_instructor:
                    self.instructors.append(self.student_dict(cr, True))
                else:
                    self.return_students.append(self.student_dict(cr, bool(cr.signature)))

    def student_dict(self, cr, is_signed):
        return {'id': cr.student.id,
                'first_name': cr.student.first_name,
                'last_name': cr.student.last_name,
                'dob': cr.student.dob,
                'check': f'check_{cr.student.id}',
                'checked': cr.attended,
                'cr_id': cr.id,
                'covid_vax': cr.student.covid_vax,
                'covid_vax_check': f'covid_vax{cr.student.id}',
                'signature': is_signed,
                'is_minor': self.crh.calc_age(cr.student, self.class_date) < 18}
