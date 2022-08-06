from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.forms import model_to_dict

from student_app.models import Student
from ..models import EventRegistration, JoadEvent, Registration, Session
import logging
logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, ListView):
    """Landing page for JOAD"""
    model = Session
    template_name = 'joad/index.html'

    def __init__(self):
        super().__init__()
        self.today = timezone.localdate(timezone.now())
        self.min_dob = self.today.replace(year=self.today.year - 21)
        self.max_dob = self.today.replace(year=self.today.year - 9)
        self.session_list = []
        self.pending = []
        self.event_list = []
        self.event_pending = []
        self.students = None
        self.has_joad = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_list'] = self.session_list
        context['has_joad'] = self.has_joad
        context['event_list'] = self.get_events()
        context['is_auth'] = len(self.students) > 0 or self.request.user.is_staff
        context['students'] = self.students
        return context

    def get_events(self):
        events = JoadEvent.objects.filter(event_date__gte=self.today).exclude(state='recorded')
        if not self.request.user.is_board:
            events = events.exclude(state='scheduled').exclude(state='canceled')
        event_list = []
        logging.debug(events)
        for event in events:
            e = model_to_dict(event)
            reg_list = []
            for student in self.students:
                reg = event.eventregistration_set.filter(student=student).order_by('id')
                reg_id = None
                reg_status = 'not registered'
                if len(reg.filter(pay_status='paid')) > 0:
                    attend = event.pinattendance_set.filter(student=student).last()
                    if attend is not None and attend.attended:
                        reg_status = 'attending'
                    else:
                        reg_status = 'registered'
                    logging.debug(attend)
                elif len(reg.filter(pay_status='start')) > 0:
                    reg_status = 'start'
                    reg_id = reg.filter(pay_status='start').last().id
                reg_list.append({'reg_status': reg_status, 'reg_id': reg_id, 'student_id': student.id})
            e['registrations'] = reg_list
            logging.debug(e)
            event_list.append(e)
        return event_list

    def get_queryset(self):
        self.students = Student.objects.get(user=self.request.user).student_family.student_set.filter(dob__gt=self.min_dob)
        self.students = self.students.filter(dob__lt=self.max_dob).order_by('last_name', 'first_name')
        sessions = Session.objects.all()
        if not self.request.user.is_staff:
            sessions = sessions.exclude(state='scheduled').exclude(state='canceled')
        sessions = sessions.exclude(state='recorded').order_by('start_date')
        self.has_joad = self.request.user.is_staff
        for session in sessions:
            s = model_to_dict(session)
            reg_list = []

            for student in self.students:
                reg_id = None
                reg_status = 'not registered'
                logging.debug(student)
                if student.is_joad:
                    self.has_joad = True
                    reg = session.registration_set.filter(student=student)#  .order_by('id')
                    logging.debug(reg)
                    if len(reg.filter(pay_status='paid')) > 0:
                        reg_status = 'registered'
                        logging.debug(reg)
                    elif len(reg.filter(pay_status='start')) > 0:
                        reg_status = 'start'
                        reg_id = reg.filter(pay_status='start').last().id
                reg_list.append({'is_joad': student.is_joad, 'reg_status': reg_status, 'reg_id': reg_id})
            s['registrations'] = reg_list
            logging.debug(s)
            self.session_list.append(s)
