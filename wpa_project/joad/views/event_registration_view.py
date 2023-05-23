from django.views.generic.edit import FormView
from django.views.generic.base import View
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from event.models import Event, Registration
from event.views.registration_view import RegistrationSuperView
from student_app.models import Student


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
        self.formset_students = kwargs['students']
        logger.warning(kwargs)
        self.get_formset()
        return kwargs

    def get_initial(self):
        eid = self.kwargs.get("event_id", None)
        logger.warning(eid)
        if eid is not None:
            event = get_object_or_404(Event, pk=eid)
            self.initial = {'event': event.id}
        return super().get_initial()

    def form_valid(self, form):
        self.form = form
        processed_formset = self.process_formset()
        if not processed_formset['success']:
            return self.has_error(self.form, processed_formset['error'])

        if self.event.state != "open": # pragma: no cover
            return self.has_error(form, 'Event in wrong state')

        # check for underage students
        of_age_date = self.event.event_date.date().replace(year=self.event.event_date.date().year - 8)
        if self.students.filter(dob__gte=of_age_date).count():
            return self.has_error(form, 'Student must be at least 8 years old to participate')

        # check for overage students
        of_age_date = self.event.event_date.date().replace(year=self.event.event_date.date().year - 21)
        if self.students.filter(dob__lt=of_age_date).count():
            return self.has_error(form, 'Student must be less then 21 years old to participate')

        if len(self.students) == 0:
            return self.has_error(form, 'Invalid student selected')

        registrations = self.event.registration_set.all()
        if len(registrations.filter(pay_status='paid')) + len(self.students) > self.event.joadevent_set.last().student_limit:
            return self.has_error(form, 'Class is full')
        # logger.warning(registrations)
        # for k, v in dict(self.request.POST).items():
        #     logger.debug(k)
        #     if str(k).startswith('student_') and v:
        #         i = int(str(k).split('_')[-1])
        #         s = Student.objects.get(pk=i)
        #         age = StudentHelper().calculate_age(s.dob, event.event_date)
        #         logger.debug(age)
        #         if age < 9:
        #             return self.has_error(form, 'Student is to young.')
        #         if age > 20:
        #             logger.debug(age)
        #             return self.has_error(form, 'Student is to old.')
        #
        #         logger.warning(s)
        #         sreg = registrations.filter(student=s)
        #         logger.warning(len(sreg))
        #         if len(sreg) == 0:
        #             students.append(s)
        #         else:
        #             messages.add_message(self.request, messages.ERROR, 'Student is already enrolled')
        #             return HttpResponseRedirect(reverse('joad:index'))


        with transaction.atomic():
            uid = str(uuid.uuid4())
            self.request.session['idempotency_key'] = uid
            self.request.session['line_items'] = []
            self.request.session['payment_category'] = 'joad'
            self.request.session['payment_description'] = f'Joad event on {str(self.event.event_date)[:10]}'
            logger.warning(self.students)
            description = f"Joad event on {str(self.event.event_date)[:10]} student: "
            for s in self.students:
                cr = self.model.objects.create(event=self.event, student=s,
                                            pay_status='start', idempotency_key=uid, user=self.request.user)
                self.request.session['line_items'].append({'name': description + f'{s.first_name}', 'quantity': 1,
                                                           'amount_each': self.event.cost_standard})
                logger.warning(cr)
        return HttpResponseRedirect(reverse('payment:make_payment'))
        # return self.form_invalid(form)


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
