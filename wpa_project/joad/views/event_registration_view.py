from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.forms import model_to_dict

from payment.src import SquareHelper
from ..forms import EventRegistrationForm
from ..models import EventRegistration, JoadEvent
from student_app.models import Student
from student_app.src import StudentHelper

import uuid
import logging
logger = logging.getLogger(__name__)


class EventRegistrationView(LoginRequiredMixin, FormView):
    template_name = 'joad/event_registration.html'
    form_class = EventRegistrationForm
    success_url = reverse_lazy('payment:process_payment')
    form = None

    def get_form(self):
        return self.form_class(user=self.request.user, **self.get_form_kwargs())

    def get_initial(self):
        eid = self.kwargs.get("event_id", None)
        if eid is not None:
            event = get_object_or_404(JoadEvent, pk=eid)
            self.initial = {'event': event}

        return super().get_initial()

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        self.form = form
        students = []
        # message = ""
        logging.debug(form.cleaned_data)
        event = form.cleaned_data['event']
        if event.state != "open":
            return self.has_error('Session in wrong state')

        reg = EventRegistration.objects.filter(event=event).exclude(
            pay_status="refunded").exclude(pay_status='canceled')
        logging.debug(len(reg.filter(pay_status='paid')))

        logging.debug(dict(self.request.POST))
        for k, v in dict(self.request.POST).items():
            logging.debug(k)
            if str(k).startswith('student_') and v:
                i = int(str(k).split('_')[-1])
                s = Student.objects.get(pk=i)
                age = StudentHelper().calculate_age(s.dob, event.event_date)
                logging.debug(age)
                if age < 9:
                    return self.has_error('Student is to young.')
                if age > 20:
                    logging.debug(age)
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
        logging.debug(len(reg.filter(pay_status='paid')))
        logging.debug(len(students))
        if len(reg.filter(pay_status='paid')) + len(students) > event.student_limit:
            return self.has_error('Class is full')

        with transaction.atomic():
            uid = str(uuid.uuid4())
            self.request.session['idempotency_key'] = uid
            self.request.session['line_items'] = []
            self.request.session['payment_db'] = ['joad', 'EventRegistration']
            self.request.session['action_url'] = reverse('programs:class_payment')
            logging.debug(students)
            description = f"Joad event on {str(event.event_date)[:10]} student id: "
            for s in students:
                cr = EventRegistration(event=event, student=s, pay_status='start', idempotency_key=uid).save()
                self.request.session['line_items'].append(
                    SquareHelper().line_item(description + f'{str(s.id)}', 1, event.cost))
                logging.debug(cr)
        return HttpResponseRedirect(reverse('payment:process_payment'))

    def has_error(self, message):
        messages.add_message(self.request, messages.ERROR, message)
        return self.form_invalid(self.form)
        # return render(self.request, self.template_name, {'form': self.form})

    def post(self, request, *args, **kwargs):
        logging.debug(self.request.POST)
        return super().post(request, *args, **kwargs)
