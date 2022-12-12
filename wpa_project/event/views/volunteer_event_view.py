from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.forms import model_to_dict
from django.utils import timezone

from ..forms import VolunteerEventForm
from ..models import VolunteerEvent

from event.models import Event
from src.mixin import BoardMixin
from student_app.models import Student

import uuid
import logging
logger = logging.getLogger(__name__)


# class EventAttendanceView(UserPassesTestMixin, SuccessMessageMixin, FormView):
#     template_name = 'joad/pin_attendance.html'
#     form_class = PinAttendanceStudentForm
#     success_url = reverse_lazy('joad:index')
#     success_message = "No pins earned today. Thank you"
#     joad_event = None
#     student = None
#     attendance = None  # if there's an attendance record for the student this will be set to that record.
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         logging.debug(self.attendance)
#         if self.attendance is not None:
#             kwargs['instance'] = self.attendance
#         return kwargs
#
#     def get_initial(self):
#         initial = super().get_initial()
#         if self.student is not None:
#             hs = self.student.pinattendance_set.high_score()
#             if hs is not None:
#                 initial['bow'] = hs.bow
#                 initial['category'] = hs.category
#                 initial['distance'] = hs.distance
#                 initial['target'] = hs.target
#                 initial['inner_scoring'] = hs.inner_scoring
#                 initial['previous_stars'] = hs.stars
#         if self.joad_event is not None and self.joad_event.event_type == 'joad_indoor':
#             choices = Choices()
#             initial['event'] = self.joad_event
#             initial['student'] = self.student
#             initial['category'] = choices.pin_shoot_catagory()[0]
#         return initial
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['student'] = f'{self.student.first_name} {self.student.last_name}'
#         return context
#
#     def form_valid(self, form):
#         logging.debug(form.cleaned_data)
#         record = form.save()
#         record.event = self.joad_event
#         record.student = self.student
#         record.category = self.joad_event.event_type
#         if self.request.user.student_set.first().student_family == self.student.student_family:
#             pins_earned = form.calculate_pins()
#             logging.debug(pins_earned)
#             if pins_earned > 0:
#                 pin_cost = self.joad_event.pin_cost
#                 if pin_cost is None:  # pragma: no cover
#                     pin_cost = 0
#                 uid = str(uuid.uuid4())
#                 self.request.session['idempotency_key'] = uid
#                 record.idempotency_key = uid
#                 record.pay_status = 'started'
#                 self.request.session['line_items'] = self.request.session.get('line_items', [])
#                 self.request.session['line_items'].append({'name': f"Joad Pin(s) for {self.student.first_name}",
#                                           'quantity': pins_earned, 'amount_each': pin_cost})
#                 self.request.session['payment_category'] = 'joad'
#                 self.request.session['payment_description'] = f'Joad Pin(s)'
#                 self.success_url = reverse('payment:make_payment')
#                 self.success_message = f'Congratulations on earning {pins_earned} pins'
#
#         record.save()
#         return super().form_valid(form)
#
#     def test_func(self):
#         eid = self.kwargs.get("event_id", None)
#         sid = self.kwargs.get('student_id', None)
#         if eid is not None and sid is not None:
#             self.joad_event = get_object_or_404(JoadEvent, pk=eid)
#             self.student = get_object_or_404(Student, pk=sid)
#             self.attendance = self.joad_event.pinattendance_set.filter(student=self.student).last()
#         if not self.request.user.is_authenticated:
#             return False
#         if self.request.user and self.request.user.is_staff:
#             self.form_class = PinAttendanceStaffForm
#             self.success_url = reverse_lazy('joad:event', kwargs={'event_id': eid})
#             return True
#         elif self.request.user.student_set.first().student_family == self.student.student_family:
#             self.form_class = PinAttendanceStudentForm
#             self.attendance = self.joad_event.pinattendance_set.filter(student=self.student).last()
#             if self.attendance is not None and self.attendance.attended:
#                 return True
#         return False


# class EventAttendListView(UserPassesTestMixin, ListView):
#     joad_event = None
#     template_name = 'joad/event_attend_list.html'
#     def get_queryset(self):
#         object_list = []
#
#         for row in self.joad_event.eventregistration_set.filter(pay_status='paid'):
#             pa = self.joad_event.pinattendance_set.filter(student=row.student).last()
#             logging.debug(pa)
#             d = {'reg': row, 'pa': pa}
#             object_list.append(d)
#         return object_list
#
#     def test_func(self):
#         if self.request.user.is_authenticated:
#             sid = self.kwargs.get("event_id", None)
#             if sid is not None:
#                 self.joad_event = get_object_or_404(JoadEvent, pk=sid)
#             return self.request.user.is_board
#         return False

class VolunteerEventListView(LoginRequiredMixin, ListView):
    template_name = 'event/volunteer_event_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['past'] = self.kwargs.get('past', False)
        return context

    def get_queryset(self):

        if self.kwargs.get('past', False):
            queryset = VolunteerEvent.objects.filter(
                event__event_date__lte=timezone.localtime(timezone.now()).date()).order_by('-event__event_date')
        else:
            queryset = VolunteerEvent.objects.filter(
                event__event_date__gte=timezone.localtime(timezone.now()).date()).order_by('event__event_date')

        return queryset


class VolunteerEventView(BoardMixin, FormView):
    template_name = 'student_app/form_as_p.html'
    form_class = VolunteerEventForm
    success_url = reverse_lazy('events:volunteer_event_list')
    volunteer_event = None

    def get_form(self):
        sid = self.kwargs.get("event_id", None)
        if sid is not None:
            self.volunteer_event = get_object_or_404(VolunteerEvent, pk=sid)
            form = self.form_class(instance=self.volunteer_event, **self.get_form_kwargs())
        else:
            form = self.form_class(**self.get_form_kwargs())
        return form

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
                state=form.cleaned_data['state'],
                type='joad event'
            )
        else:
            event.event.event_date = form.cleaned_data['event_date']
            event.event.state = form.cleaned_data['state']
            event.event.save()
        event.save()
        return super().form_valid(form)
