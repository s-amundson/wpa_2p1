from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.forms import model_to_dict

from student_app.models import Student
from ..models import JoadEvent, Session
import logging
logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, View):
    """Landing page for JOAD"""
    def get(self, request):
        today = timezone.localdate(timezone.now())
        min_dob = today.replace(year=today.year - 21)
        max_dob = today.replace(year=today.year - 9)
        students = Student.objects.get(user=request.user).student_family.student_set.filter(dob__gt=min_dob)
        students = students.filter(dob__lt=max_dob).order_by('last_name', 'first_name')
        sessions = Session.objects.all()
        if not request.user.is_staff:
            sessions = sessions.exclude(state='scheduled').exclude(state='canceled').exclude(state='recorded')
        sessions = sessions.order_by('start_date')
        session_list = []
        has_joad = request.user.is_staff
        for session in sessions:
            s = model_to_dict(session)
            reg_list = []
            for student in students:
                if student.is_joad:
                    has_joad = True
                    reg = session.registration_set.filter(student=student, pay_status='paid')
                    if len(reg) > 0:
                        logging.debug(reg)
                    reg_list.append({'is_joad': student.is_joad, 'reg': len(reg) > 0})
                else:
                    reg_list.append({'is_joad': student.is_joad, 'reg': False})
            s['registrations'] = reg_list
            logging.debug(s)
            session_list.append(s)
        is_auth = len(students) > 0 or request.user.is_staff
        events = JoadEvent.objects.filter(event_date__gte=today)
        if not request.user.is_board:
            events = events.exclude(state='scheduled').exclude(state='canceled').exclude(state='recorded')
        event_list = []
        for event in events:
            e = model_to_dict(event)
            reg_list = []
            for student in students:
                reg = event.eventregistration_set.filter(student=student)
                reg_status = 'not registered'
                if len(reg.filter(pay_status='paid')) > 0:
                    attend = event.pinattendance_set.filter(student=student).last()
                    if attend is not None and attend.attended:
                        reg_status = 'attending'
                    else:
                        reg_status = 'registered'
                    logging.debug(attend)
                reg_list.append({'reg_status': reg_status, 'student_id': student.id})
            e['registrations'] = reg_list
            logging.debug(e)
            event_list.append(e)
        return render(request, 'joad/index.html',
                      {'session_list': session_list, 'students': students, 'has_joad': has_joad, 'is_auth': is_auth,
                       'event_list': event_list})
