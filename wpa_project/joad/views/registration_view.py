from django.views.generic.edit import FormView
from django.views.generic.base import View
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from ..forms import RegistrationForm
from ..models import Registration, Session
from student_app.models import Student
from student_app.src import StudentHelper

import uuid
import logging
logger = logging.getLogger(__name__)


class RegistrationSuperView(UserPassesTestMixin, FormView):
    template_name = 'joad/registration.html'
    form_class = RegistrationForm
    session = None
    success_url = reverse_lazy('payment:make_payment')
    form = None

    def get_initial(self):
        self.initial = {'session': self.session}

        return super().get_initial()

    def form_invalid(self, form):
        logger.debug(form.errors)
        return super().form_invalid(form)

    def has_error(self, message):
        messages.add_message(self.request, messages.ERROR, message)
        return self.form_invalid(self.form)

    def post(self, request, *args, **kwargs):
        logger.debug(self.request.POST)
        return super().post(request, *args, **kwargs)

    def test_func(self):
        if self.request.user.is_authenticated:
            if self.request.user.student_set.first().student_family is None:
                return False
            sid = self.kwargs.get("session_id", None)
            if sid is not None:
                self.session = get_object_or_404(Session, pk=sid)
            return True
        else:
            return False


class RegistrationView(RegistrationSuperView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.has_perm('student_app.board'):
            kwargs['students'] = Student.objects.filter(is_joad=True)
        else:
            kwargs['students'] = self.request.user.student_set.first().student_family.student_set.filter(is_joad=True)

        return kwargs

    def form_valid(self, form):
        self.form = form
        students = []
        # message = ""
        logger.debug(form.cleaned_data['session'])
        session = form.cleaned_data['session']
        if session.state != "open":  # pragma: no cover
            return self.has_error('Session in wrong state')

        reg = session.registration_set.exclude(pay_status="refunded").exclude(pay_status='canceled')
        logger.debug(len(reg.filter(pay_status='paid')))

        for k, v in form.cleaned_data.items():
            logger.debug(k)
            if str(k).startswith('student_') and v:
                i = int(str(k).split('_')[-1])
                s = Student.objects.get(pk=i)
                age = StudentHelper().calculate_age(s.dob, session.start_date)
                logger.debug(age)
                if age < 9:
                    return self.has_error('Student is to young')
                if age > 20: # pragma: no cover
                    return self.has_error('Student is to old.')

                logger.debug(s)
                sreg = reg.filter(student=s)
                logger.debug(len(sreg))
                if len(sreg) == 0:
                    students.append(s)
                else:
                    return self.has_error('Student is already enrolled')

        if len(students) == 0:
            return self.has_error('Invalid student selected')

        if len(reg.filter(pay_status='paid')) + len(students) > session.student_limit:
            return self.has_error('Class is full')

        with transaction.atomic():
            uid = str(uuid.uuid4())
            self.request.session['idempotency_key'] = uid
            self.request.session['line_items'] = []
            self.request.session['payment_category'] = 'joad'
            self.request.session['payment_description'] = f'Joad session starting {str(session.start_date)[:10]}'
            logger.debug(students)
            for s in students:
                cr = Registration(session=session, student=s, pay_status='start', idempotency_key=uid).save()
                self.request.session['line_items'].append(
                    {'name': f'Joad session starting {str(session.start_date)[:10]} student id: {str(s.id)}',
                     'quantity': 1, 'amount_each': session.cost})
                logger.debug(cr)
        return HttpResponseRedirect(reverse('payment:make_payment'))


class ResumeRegistrationView(LoginRequiredMixin, View):
    def get(self, request, reg_id=None):
        registration = get_object_or_404(Registration, pk=reg_id)
        registrations = Registration.objects.filter(idempotency_key=registration.idempotency_key)
        logger.debug(registration)
        self.request.session['idempotency_key'] = str(registration.idempotency_key)
        self.request.session['line_items'] = []
        self.request.session['payment_category'] = 'joad'

        for r in registrations:
            self.request.session['payment_description'] = f'Joad session starting {str(r.session.start_date)[:10]}'
            self.request.session['line_items'].append(
                    {'name': f'Joad session starting {str(r.session.start_date)[:10]} student id: {str(r.student.id)}',
                     'quantity': 1, 'amount_each': r.session.cost})
        return HttpResponseRedirect(reverse('payment:make_payment'))


class RegistrationCancelView(RegistrationSuperView):
    success_url = reverse_lazy('joad:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.has_perm('student_app.board'):
            students = Student.objects.filter(is_joad=True)
        else:
            students = self.request.user.student_set.last().student_family.student_set.filter(is_joad=True)
        logger.debug(students)
        kwargs['students'] = students.filter(session_registration__in=self.session.registration_set.all())
        kwargs['cancel'] = True
        logger.debug(kwargs)
        return kwargs

    def form_valid(self, form):
        logger.debug(form.cleaned_data)
        if form.process_refund(self.request.user):
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def test_func(self):
        if super().test_func():
            return self.session is not None
        return False
