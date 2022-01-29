from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.forms import model_to_dict
from django.http import Http404
from django.utils import timezone

from ..forms import JoadEventForm, PinAttendanceStaffForm, PinAttendanceStudentForm
from ..models import JoadEvent, PinAttendance
from ..src import Choices
from student_app.models import Student

import logging
logger = logging.getLogger(__name__)


class EventAttendanceView(LoginRequiredMixin, FormView):
    template_name = 'joad/pin_attendance.html'
    form_class = PinAttendanceStudentForm
    success_url = reverse_lazy('joad:index')
    event = None
    student = None

    def get_form(self):
        eid = self.kwargs.get("event_id", None)
        sid = self.kwargs.get('student_id', None)
        if eid is not None and sid is not None:
            self.event = get_object_or_404(JoadEvent, pk=eid)
            self.student = get_object_or_404(Student, pk=sid)
            if self.event.event_type == 'Pin Shoot':
                choices = Choices()
                self.initial = {'event': self.event, 'student': self.student, 'category': choices.pin_shoot_catagory()[0]}
                # initial =
                if self.request.user.is_staff:
                    self.form_class = PinAttendanceStaffForm
                elif self.requst.user.student.student_family == self.student.student_family:
                    self.form_class = PinAttendanceStudentForm
                else:
                    raise Http404("Event or student not found.")
        return self.form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = f'{self.student.first_name} {self.student.last_name}'
        return context

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        record = form.save()
        record.event = self.event
        record.student = self.student
        record.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        logging.debug(self.request.POST)

        return super().post(request, *args, **kwargs)


class JoadEventView(UserPassesTestMixin, FormView):
    template_name = 'joad/event.html'
    form_class = JoadEventForm
    success_url = reverse_lazy('joad:index')
    event = None

    def get_form(self):
        sid = self.kwargs.get("event_id", None)
        if sid is not None:
            self.event = get_object_or_404(JoadEvent, pk=sid)
            form = self.form_class(instance=self.event, **self.get_form_kwargs())
        else:
            form = self.form_class(**self.get_form_kwargs())
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_list = []
        if self.event is not None:
            for reg in self.event.eventregistration_set.filter(pay_status='paid'):
                s = model_to_dict(reg.student)
                attendance = PinAttendance.objects.filter(event=self.event, student=reg.student)
                s['attend_record'] = len(attendance) > 0
                s['attend'] = False
                logging.debug(s['attend_record'])
                if len(attendance) > 0:
                    s['attend'] = attendance[0].attended
                student_list.append(s)

        context['student_list'] = student_list
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_board
