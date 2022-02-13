from django import forms
from django.db.models import Q
from student_app.src import StudentHelper
import logging

logger = logging.getLogger(__name__)


class ClassAttendanceForm(forms.Form):

    def __init__(self, beginner_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_helper = StudentHelper()
        self.is_closed = beginner_class.state == 'closed'
        self.new_students = []
        self.return_students = []
        self.staff = []
        self.class_registration = beginner_class.classregistration_set.filter(
            Q(pay_status='paid') | Q(pay_status='admin'))
        self.class_registration = self.class_registration.order_by('attended', 'student__last_name')
        self.class_date = beginner_class.class_date
        self.attend_count = {'beginner': 0, 'returnee': 0, 'staff': 0}

        for cr in self.class_registration:
            try:
                is_staff = cr.student.user.is_staff
            except (cr.student.DoesNotExist, AttributeError):
                is_staff = False
            if is_staff:
                self.staff.append(self.student_dict(cr, True))
                if cr.attended:
                    self.attend_count['staff'] += 1
            elif cr.student.safety_class is None or cr.student.safety_class <= self.class_date.date():
                self.new_students.append(self.student_dict(cr, bool(cr.student.signature)))
                if cr.attended:
                    self.attend_count['beginner'] += 1
            else:
                self.return_students.append(self.student_dict(cr, bool(cr.student.signature)))
                if cr.attended:
                    self.attend_count['returnee'] += 1

    def student_dict(self, cr, is_signed):
        # logging.debug(f'student: {cr.student.id} vax: {cr.student.covid_vax}, attended:{cr.attended}')
        return {'id': cr.student.id,
                'first_name': cr.student.first_name,
                'last_name': cr.student.last_name,
                'dob': cr.student.dob,
                'check': f'check_{cr.student.id}',
                'checked': cr.attended,
                'cr_id': cr.id,
                'covid_vax': cr.student.covid_vax,
                'covid_vax_check': f'covid_vax_{cr.student.id}',
                'signature': is_signed,
                'is_minor': self.student_helper.calculate_age(cr.student.dob, self.class_date) < 18}
