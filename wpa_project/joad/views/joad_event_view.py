from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.forms import model_to_dict
from django.utils import timezone

from ..forms import JoadEventForm, PinAttendanceStaffForm, PinAttendanceStudentForm
from ..models import JoadEvent, PinAttendance
from ..src import Choices
from event.models import Event
from src.mixin import BoardMixin
from student_app.models import Student

import uuid
import logging
logger = logging.getLogger(__name__)


class EventAttendanceView(UserPassesTestMixin, SuccessMessageMixin, FormView):
    template_name = 'joad/pin_attendance.html'
    form_class = PinAttendanceStudentForm
    success_url = reverse_lazy('joad:index')
    success_message = "No pins earned today. Thank you"
    joad_event = None
    student = None
    attendance = None  # if there's an attendance record for the student this will be set to that record.

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        logging.debug(self.attendance)
        if self.attendance is not None:
            kwargs['instance'] = self.attendance
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if self.student is not None:
            hs = self.student.pinattendance_set.high_score()
            if hs is not None:
                initial['bow'] = hs.bow
                initial['category'] = hs.category
                initial['distance'] = hs.distance
                initial['target'] = hs.target
                initial['inner_scoring'] = hs.inner_scoring
                initial['previous_stars'] = hs.stars
        if self.joad_event is not None and self.joad_event.event_type == 'joad_indoor':
            choices = Choices()
            initial['event'] = self.joad_event
            initial['student'] = self.student
            initial['category'] = choices.pin_shoot_catagory()[0]
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = f'{self.student.first_name} {self.student.last_name}'
        return context

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        record = form.save()
        record.event = self.joad_event
        record.student = self.student
        record.category = self.joad_event.event_type
        if self.request.user.student_set.first().student_family == self.student.student_family:
            pins_earned = form.calculate_pins()
            logging.debug(pins_earned)
            if pins_earned > 0:
                pin_cost = self.joad_event.pin_cost
                if pin_cost is None:  # pragma: no cover
                    pin_cost = 0
                uid = str(uuid.uuid4())
                self.request.session['idempotency_key'] = uid
                record.idempotency_key = uid
                record.pay_status = 'started'
                self.request.session['line_items'] = self.request.session.get('line_items', [])
                self.request.session['line_items'].append({'name': f"Joad Pin(s) for {self.student.first_name}",
                                          'quantity': pins_earned, 'amount_each': pin_cost})
                self.request.session['payment_category'] = 'joad'
                self.request.session['payment_description'] = f'Joad Pin(s)'
                self.success_url = reverse('payment:make_payment')
                self.success_message = f'Congratulations on earning {pins_earned} pins'

        record.save()
        return super().form_valid(form)

    def test_func(self):
        eid = self.kwargs.get("event_id", None)
        sid = self.kwargs.get('student_id', None)
        if eid is not None and sid is not None:
            self.joad_event = get_object_or_404(JoadEvent, pk=eid)
            self.student = get_object_or_404(Student, pk=sid)
            self.attendance = self.joad_event.pinattendance_set.filter(student=self.student).last()
        if not self.request.user.is_authenticated:
            return False
        if self.request.user and self.request.user.is_staff:
            self.form_class = PinAttendanceStaffForm
            self.success_url = reverse_lazy('joad:event', kwargs={'event_id': eid})
            return True
        elif self.request.user.student_set.first().student_family == self.student.student_family:
            self.form_class = PinAttendanceStudentForm
            self.attendance = self.joad_event.pinattendance_set.filter(student=self.student).last()
            if self.attendance is not None and self.attendance.attended:
                return True
        return False


class EventAttendListView(UserPassesTestMixin, ListView):
    joad_event = None
    template_name = 'joad/event_attend_list.html'
    def get_queryset(self):
        object_list = []

        for row in self.joad_event.event.registration_set.filter(pay_status__in=['paid', 'admin']):
            pa = self.joad_event.pinattendance_set.filter(student=row.student).last()
            logging.debug(pa)
            d = {'reg': row, 'pa': pa}
            object_list.append(d)
        return object_list

    def test_func(self):
        if self.request.user.is_authenticated:
            sid = self.kwargs.get("event_id", None)
            if sid is not None:
                self.joad_event = get_object_or_404(JoadEvent, pk=sid)
            return self.request.user.is_board
        return False


class JoadEventListView(UserPassesTestMixin, ListView):
    model = JoadEvent
    template_name = 'joad/event_list.html'

    def __init__(self):
        super().__init__()
        self.today = timezone.localdate(timezone.now())
        self.min_dob = self.today.replace(year=self.today.year - 21)
        self.max_dob = self.today.replace(year=self.today.year - 9)
        self.past_events = True
        self.students = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_list'] = self.get_events()
        context['past_events'] = self.past_events
        return context

    def get_events(self):
        if self.past_events:
            events = JoadEvent.objects.filter(event__event_date__lt=self.today)
        else:
            events = JoadEvent.objects.filter(event__event_date__gte=self.today)
        events = events.exclude(event__state='recorded')
        if not self.request.user.is_board:
            events = events.exclude(event__state='scheduled').exclude(event__state='canceled')
        event_list = []
        logging.debug(events)
        for event in events:
            e = model_to_dict(event)
            reg_list = []
            if self.students:
                for student in self.students:
                    reg = event.event.registration_set.filter(student=student).order_by('id')
                    reg_id = None
                    reg_status = 'closed'
                    if len(reg.filter(pay_status='paid')) > 0:
                        attend = event.pinattendance_set.filter(student=student).last()
                        if attend is not None and attend.attended:
                            reg_status = 'attending'
                        else:
                            reg_status = 'registered'
                        logging.debug(attend)
                    elif len(reg.filter(pay_status='start')) > 0 and event.event.state in ['open', 'full']:
                        reg_status = 'start'
                        reg_id = reg.filter(pay_status='start').last().id
                    elif event.event.state in ['open', 'full']:
                        reg_status = 'not registered'
                    reg_list.append({'reg_status': reg_status, 'reg_id': reg_id, 'student_id': student.id})
            e['registrations'] = reg_list
            e['event_date'] = event.event.event_date
            e['state'] = event.event.state
            e['cost'] = event.event.cost_standard
            logging.debug(e)
            event_list.append(e)
        return event_list

    def test_func(self):
        if self.request.user.is_authenticated:
            student = self.request.user.student_set.last()
            if student and student.student_family:
                self.students = student.student_family.student_set.filter(
                    dob__gt=self.min_dob, dob__lt=self.max_dob).order_by('last_name', 'first_name')
            return True
        return False


class JoadEventView(BoardMixin, FormView):
    template_name = 'joad/event.html'
    form_class = JoadEventForm
    success_url = reverse_lazy('joad:index')
    joad_event = None

    def get_form(self):
        sid = self.kwargs.get("event_id", None)
        if sid is not None:
            self.joad_event = get_object_or_404(JoadEvent, pk=sid)
            form = self.form_class(instance=self.joad_event, **self.get_form_kwargs())
        else:
            form = self.form_class(**self.get_form_kwargs())
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_list = []
        if self.joad_event is not None:
            for reg in self.joad_event.event.registration_set.filter(pay_status='paid'):
                s = model_to_dict(reg.student)
                attendance = PinAttendance.objects.filter(event=self.joad_event, student=reg.student)
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
        event = form.save()
        logging.warning(event)
        if event.event is None:
            event.event = Event.objects.create(
                event_date=form.cleaned_data['event_date'],
                cost_standard=form.cleaned_data['cost'],
                cost_member=form.cleaned_data['cost'],
                state=form.cleaned_data['state'],
                type='joad event'
            )
        else:
            event.event.event_date = form.cleaned_data['event_date']
            event.event.cost_standard = form.cleaned_data['cost']
            event.event.cost_member = form.cleaned_data['cost']
            event.event.state = form.cleaned_data['state']
            event.event.save()
        event.save()
        return super().form_valid(form)
