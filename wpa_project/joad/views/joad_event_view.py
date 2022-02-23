from django.views.generic.edit import FormView
from django.contrib.auth.mixins import  UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.forms import model_to_dict

from ..forms import JoadEventForm, PinAttendanceStaffForm, PinAttendanceStudentForm
from ..models import JoadEvent, PinAttendance
from ..src import Choices
from payment.models import CostsModel
from payment.src import SquareHelper
from student_app.models import Student

import uuid
import logging
logger = logging.getLogger(__name__)


class EventAttendanceView(UserPassesTestMixin, SuccessMessageMixin, FormView):
    template_name = 'joad/pin_attendance.html'
    form_class = PinAttendanceStudentForm
    success_url = reverse_lazy('joad:index')
    success_message = "No pins earned today. Thank you"
    event = None
    student = None
    attendance = None  # if there's an attendance record for the student this will be set to that record.

    def get_form(self):
        if self.attendance is not None:
            return self.form_class(instance=self.attendance, **self.get_form_kwargs())
        if self.event is not None and self.event.event_type == 'joad_indoor':
            choices = Choices()
            self.initial = {'event': self.event, 'student': self.student, 'category': choices.pin_shoot_catagory()[0]}
        return self.form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = f'{self.student.first_name} {self.student.last_name}'
        return context

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        record = form.save()
        record.event = self.event
        record.student = self.student
        record.category = self.event.event_type
        if self.request.user.student_set.first().student_family == self.student.student_family:
            pins_earned = form.calculate_pins()
            logging.debug(pins_earned)
            if pins_earned > 0:
                pin_cost = CostsModel.objects.filter(name='JOAD Pin', enabled=True)
                if pin_cost is not None:
                    pin_cost = pin_cost[0].standard_cost
                else: # pragma: no cover
                    pin_cost = 6
                uid = str(uuid.uuid4())
                self.request.session['idempotency_key'] = uid
                self.request.session['line_items'] = []
                self.request.session['payment_db'] = ['joad', 'PinAttendance']
                # self.request.session['action_url'] = reverse('programs:class_payment')
                record.idempotency_key = uid
                record.pay_status = 'started'
                self.request.session['line_items'].append(SquareHelper().line_item(
                        f"Joad Pin(s) for {self.student.first_name}", pins_earned, pin_cost))
                self.success_url = reverse('payment:process_payment')
                self.success_message = f'Congratulations on earning {pins_earned} pins'

        record.save()
        return super().form_valid(form)

    def test_func(self):
        eid = self.kwargs.get("event_id", None)
        sid = self.kwargs.get('student_id', None)
        if eid is not None and sid is not None:
            self.event = get_object_or_404(JoadEvent, pk=eid)
            self.student = get_object_or_404(Student, pk=sid)
            self.attendance = self.event.pinattendance_set.filter(student=self.student).last()

        if self.request.user.is_staff:
            self.form_class = PinAttendanceStaffForm
            self.success_url = reverse_lazy('joad:event', kwargs={'event_id': eid})
            return True
        elif self.request.user.student_set.first().student_family == self.student.student_family:
            self.form_class = PinAttendanceStudentForm
            self.attendance = self.event.pinattendance_set.filter(student=self.student).last()
            if self.attendance is not None and self.attendance.attended:
                return True
        return False


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

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        form.save()
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_board
