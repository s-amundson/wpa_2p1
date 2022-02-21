from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from payment.src import SquareHelper
from ..forms import RegistrationForm
from ..models import Registration, Session
from student_app.models import Student
from student_app.src import StudentHelper

import uuid
import logging
logger = logging.getLogger(__name__)


class RegistrationView(UserPassesTestMixin, FormView):
    template_name = 'joad/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('payment:process_payment')
    form = None

    def get_form(self):
        return RegistrationForm(user=self.request.user, **self.get_form_kwargs())

    def get_initial(self):
        sid = self.kwargs.get("session_id", None)
        if sid is not None:
            session = get_object_or_404(Session, pk=sid)
            self.initial = {'session': session}

        return super().get_initial()

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        self.form = form
        students = []
        # message = ""
        logging.debug(form.cleaned_data['session'])
        session = form.cleaned_data['session']
        if session.state != "open": # pragma: no cover
            return self.has_error('Session in wrong state')

        reg = Registration.objects.filter(session=session).exclude(
            pay_status="refunded").exclude(pay_status='canceled')
        logging.debug(len(reg.filter(pay_status='paid')))

        for k, v in form.cleaned_data.items():
            logging.debug(k)
            if str(k).startswith('student_') and v:
                i = int(str(k).split('_')[-1])
                s = Student.objects.get(pk=i)
                age = StudentHelper().calculate_age(s.dob, session.start_date)
                logging.debug(age)
                if age < 9:
                    return self.has_error('Student is to young')
                if age > 20: # pragma: no cover
                    return self.has_error('Student is to old.')

                logging.debug(s)
                sreg = reg.filter(student=s)
                logging.debug(len(sreg))
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
            self.request.session['payment_db'] = ['joad', 'Registration']
            self.request.session['action_url'] = reverse('programs:class_payment')
            logging.debug(students)
            for s in students:
                cr = Registration(session=session, student=s, pay_status='start', idempotency_key=uid).save()
                self.request.session['line_items'].append(
                    SquareHelper().line_item(f"Joad session starting {str(session.start_date)[:10]} student id: {str(s.id)}",
                                             1, session.cost))
                logging.debug(cr)
        return HttpResponseRedirect(reverse('payment:process_payment'))

    def has_error(self, message):
        messages.add_message(self.request, messages.ERROR, message)
        return self.form_invalid(self.form)
        # return render(self.request, self.template_name, {'form': self.form})

    def post(self, request, *args, **kwargs):
        logging.debug(self.request.POST)
        return super().post(request, *args, **kwargs)

    def test_func(self):
        if self.request.user.is_authenticated:
            if self.request.user.student_set.first().student_family is None:
                # return HttpResponseRedirect(reverse('registration:profile'))
                return False
            return True
        else:
            return False
