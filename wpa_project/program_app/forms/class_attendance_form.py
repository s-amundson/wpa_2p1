from django import forms
from django.db.models import Q
from student_app.src import StudentHelper

from student_app.models import Student

import logging
logger = logging.getLogger(__name__)


class ClassAttendanceForm(forms.Form):

    def __init__(self, beginner_class, *args, **kwargs):
        self.beginner_class = beginner_class
        super().__init__(*args, **kwargs)
        staff = Student.objects.filter(user__is_staff=True)
        self.student_helper = StudentHelper()
        self.is_closed = beginner_class.state == 'closed'
        registrations = beginner_class.classregistration_set.filter(
            pay_status__in=['admin', 'comped', 'paid', 'waiting']).order_by('attended', 'student__last_name')
        self.class_date = beginner_class.class_date

        self.adult_dob = self.class_date.date().replace(year=self.class_date.year - 18)
        logging.debug(self.adult_dob)

        self.new_students = registrations.exclude(student__in=staff).filter(
            Q(student__safety_class__isnull=True) | Q(student__safety_class__gte=self.class_date.date()))
        self.new_students_waiting = self.new_students.filter(pay_status='waiting')
        self.new_students = self.new_students.exclude(pay_status='waiting')
        self.staff = registrations.filter(student__in=staff)
        self.return_students = registrations.exclude(student__in=staff).filter(
            student__safety_class__lt=self.class_date.date())
        self.return_students_waiting = self.return_students.filter(pay_status='waiting')
        self.return_students = self.return_students.exclude(pay_status='waiting')

        logging.debug(self.new_students)
        self.attend_count = {'beginner': len(self.new_students.filter(attended=True)),
                             'returnee': len(self.return_students.filter(attended=True)),
                             'staff': len(self.staff.filter(attended=True))}

