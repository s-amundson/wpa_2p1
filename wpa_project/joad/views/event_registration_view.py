from django.views.generic.edit import FormView
from django.views.generic.base import View
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

# from ..models import EventRegistration, JoadEvent
from event.models import Event, Registration
from event.views.registration_view import RegistrationSuperView
from student_app.models import Student
from student_app.src import StudentHelper

import uuid
import logging
logger = logging.getLogger(__name__)


class EventRegistrationView(RegistrationSuperView):
    template_name = 'joad/event_registration.html'
    event_type = 'joad event'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_board:
            kwargs['students'] = Student.objects.filter(is_joad=True)
        else:
            kwargs['students'] = kwargs['students'].filter(is_joad=True)
        return kwargs

    def get_initial(self):
        eid = self.kwargs.get("event_id", None)
        if eid is not None:
            event = get_object_or_404(Event, pk=eid)
            self.initial = {'event': event.id}
        return super().get_initial()

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        students = []
        event = form.cleaned_data['event']
        if event.state != "open": # pragma: no cover
            return self.has_error(form, 'Event in wrong state')
        registrations = event.registration_set.all()
        logger.warning(registrations)
        for k, v in dict(self.request.POST).items():
            logger.debug(k)
            if str(k).startswith('student_') and v:
                i = int(str(k).split('_')[-1])
                s = Student.objects.get(pk=i)
                age = StudentHelper().calculate_age(s.dob, event.event_date)
                logger.debug(age)
                if age < 9:
                    return self.has_error(form, 'Student is to young.')
                if age > 20:
                    logger.debug(age)
                    return self.has_error(form, 'Student is to old.')

                logger.warning(s)
                sreg = registrations.filter(student=s)
                logger.warning(len(sreg))
                if len(sreg) == 0:
                    students.append(s)
                else:
                    messages.add_message(self.request, messages.ERROR, 'Student is already enrolled')
                    return HttpResponseRedirect(reverse('joad:index'))
        if len(students) == 0:
            return self.has_error(form, 'Invalid student selected')

        if len(registrations.filter(pay_status='paid')) + len(students) > event.joadevent_set.last().student_limit:
            return self.has_error(form, 'Class is full')

        with transaction.atomic():
            uid = str(uuid.uuid4())
            self.request.session['idempotency_key'] = uid
            self.request.session['line_items'] = []
            self.request.session['payment_category'] = 'joad'
            self.request.session['payment_description'] = f'Joad event on {str(event.event_date)[:10]}'
            logger.warning(students)
            description = f"Joad event on {str(event.event_date)[:10]} student: "
            for s in students:
                cr = self.model.objects.create(event=event, student=s,
                                            pay_status='start', idempotency_key=uid, user=self.request.user)
                self.request.session['line_items'].append({'name': description + f'{s.first_name}', 'quantity': 1,
                                                           'amount_each': event.cost_standard})
                logger.warning(cr)
        return HttpResponseRedirect(reverse('payment:make_payment'))
        # return self.form_invalid(form)
# class EventRegistrationView(LoginRequiredMixin, FormView):
#     template_name = 'joad/event_registration.html'
#     form_class = EventRegistrationForm
#     success_url = reverse_lazy('payment:make_payment')
#     form = None
#
#     def get_form(self):
#         return self.form_class(user=self.request.user, **self.get_form_kwargs())
#
#     def get_initial(self):
#         eid = self.kwargs.get("event_id", None)
#         if eid is not None:
#             event = get_object_or_404(Event, pk=eid)
#             je = event.joadevent_set.last()
#             logger.warning(je.id)
#             self.initial = {'joad_event': je}
#
#         return super().get_initial()
#
#     def form_invalid(self, form):
#         logger.debug(form.errors)
#         return super().form_invalid(form)
#
#     def form_valid(self, form):
#         self.form = form
#         students = []
#         # message = ""
#         logger.warning(form.cleaned_data)
#         joad_event = form.cleaned_data['joad_event']
#         logger.debug(joad_event.event.state)
#         logger.debug(joad_event.id)
#         if joad_event.event.state != "open": # pragma: no cover
#             return self.has_error('Event in wrong state')
#
#         reg = EventRegistration.objects.filter(joad_event=joad_event).exclude(
#             pay_status="refunded").exclude(pay_status='canceled')
#         logger.debug(len(reg.filter(pay_status='paid')))
#
#         logger.debug(dict(self.request.POST))
#         for k, v in dict(self.request.POST).items():
#             logger.debug(k)
#             if str(k).startswith('student_') and v:
#                 i = int(str(k).split('_')[-1])
#                 s = Student.objects.get(pk=i)
#                 age = StudentHelper().calculate_age(s.dob, joad_event.event.event_date)
#                 logger.debug(age)
#                 if age < 9:
#                     return self.has_error('Student is to young.')
#                 if age > 20:
#                     logger.debug(age)
#                     return self.has_error('Student is to old.')
#
#                 logger.debug(s)
#                 sreg = reg.filter(student=s)
#                 logger.debug(len(sreg))
#                 if len(sreg) == 0:
#                     students.append(s)
#                 else:
#                     messages.add_message(self.request, messages.ERROR, 'Student is already enrolled')
#                     return HttpResponseRedirect(reverse('joad:index'))
#
#         if len(students) == 0:
#             return self.has_error('Invalid student selected')
#         logger.debug(len(reg.filter(pay_status='paid')))
#         logging.debug(len(students))
#         if len(reg.filter(pay_status='paid')) + len(students) > joad_event.student_limit:
#             return self.has_error('Class is full')
#
#         with transaction.atomic():
#             uid = str(uuid.uuid4())
#             self.request.session['idempotency_key'] = uid
#             self.request.session['line_items'] = []
#             self.request.session['payment_category'] = 'joad'
#             self.request.session['payment_description'] = f'Joad event on {str(joad_event.event.event_date)[:10]}'
#             logging.warning(students)
#             description = f"Joad event on {str(joad_event.event.event_date)[:10]} student: "
#             for s in students:
#                 cr = EventRegistration(joad_event=joad_event, student=s, pay_status='start', idempotency_key=uid).save()
#                 self.request.session['line_items'].append({'name': description + f'{s.first_name}', 'quantity': 1,
#                                                            'amount_each': joad_event.event.cost_standard})
#                 logging.warning(cr)
#         return HttpResponseRedirect(reverse('payment:make_payment'))
#
#     def has_error(self, message):
#         messages.add_message(self.request, messages.ERROR, message)
#         return self.form_invalid(self.form)
#         # return render(self.request, self.template_name, {'form': self.form})


class ResumeEventRegistrationView(LoginRequiredMixin, View):
    def get(self, request, reg_id=None):
        registration = get_object_or_404(Registration, pk=reg_id)
        registrations = Registration.objects.filter(idempotency_key=registration.idempotency_key)
        logger.debug(registration)
        self.request.session['idempotency_key'] = str(registration.idempotency_key)
        self.request.session['line_items'] = []
        self.request.session['payment_category'] = 'joad'
        for r in registrations:
            description = f"Joad event on {str(registration.event.event_date)[:10]} student: "
            self.request.session['line_items'].append({'name': description + f'{r.student.first_name}', 'quantity': 1,
                                                           'amount_each': r.event.cost_standard})
        return HttpResponseRedirect(reverse('payment:make_payment'))
