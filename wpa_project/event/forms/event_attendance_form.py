from django import forms
from django.db.models import Q

from student_app.src import StudentHelper
from student_app.models import Student
from src.years import sub_years

import logging
logger = logging.getLogger(__name__)


class EventAttendanceForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        super().__init__(*args, **kwargs)
        staff = Student.objects.filter(user__is_staff=True)
        self.student_helper = StudentHelper()
        self.is_closed = self.event.state == 'closed'
        registrations = self.event.registration_set.filter(
            Q(pay_status__in=['admin', 'comped', 'paid']) | Q(pay_status__startswith='wait')).order_by(
            'attended', 'student__last_name')
        self.class_date = self.event.event_date

        # self.adult_dob = self.class_date.date().replace(year=self.class_date.year - 18)
        self.adult_dob = sub_years(self.class_date.date(), 18)
        self.new_students = registrations.exclude(student__in=staff)
        self.new_students_waiting = self.new_students.filter(pay_status__in=['waiting', 'waiting_error'])
        if self.event.type != 'work':
            self.new_students = self.new_students.filter(
                Q(student__safety_class__isnull=True) | Q(student__safety_class__gte=self.class_date.date()))
            self.new_students_waiting = self.new_students.filter(pay_status__startswith='wait')
            self.new_students = self.new_students.exclude(pay_status__startswith='wait')
        self.staff = registrations.filter(student__in=staff)
        self.return_students = registrations.exclude(student__in=staff).filter(
            student__safety_class__lt=self.class_date.date())
        self.return_students_waiting = self.return_students.filter(pay_status__startswith='wait')
        self.return_students = self.return_students.exclude(pay_status__startswith='wait')

        self.attend_count = {'beginner': len(self.new_students.filter(attended=True)),
                             'returnee': len(self.return_students.filter(attended=True)),
                             'staff': len(self.staff.filter(attended=True))}
        self.admit_statuses = ['paid', 'admin']
