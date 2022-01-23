from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from allauth.account.models import EmailAddress
from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views import View
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic.base import View

from payment.src import SquareHelper
from ..forms import RegistrationForm
from ..models import Registration, Session
from student_app.models import Student

import uuid
import logging
logger = logging.getLogger(__name__)


# class RegistrationView(LoginRequiredMixin, FormView):
#     template_name = 'joad/registration.html'
#     form_class = RegistrationForm
#     success_url = reverse_lazy('payment:index')
#
#     def get_form(self):
#
#         return RegistrationForm(user=self.request.user, **self.get_form_kwargs())
#
#     def get_initial(self):
#         if self.request.user:
#             student = Student.objects.get(user=self.request.user)
#             self.initial = {'contact_name': f'{student.first_name} {student.last_name}',
#                        'email': EmailAddress.objects.get_primary(self.request.user)}
#         return super().get_initial()
#
#     def form_invalid(self, form):
#         logging.debug(form.errors)
#         return super().form_invalid(form)
#
#     def form_valid(self, form):
#         students = []
#         # message = ""
#         logging.debug(form.cleaned_data['session'])
#         session = form.cleaned_data['session']
#         if session.state != "open":
#             messages.add_message(self.request, messages.ERROR,
#                                  'Session in wrong state')
#             # message += 'Session in wrong state'
#             return self.form_invalid(self.get_form())
#         reg = Registration.objects.filter(session=session).exclude(
#             pay_status="refunded").exclude(pay_status='canceled')
#         logging.debug(len(reg.filter(pay_status='paid')))
#
#         for k, v in form.cleaned_data.items():
#             logging.debug(k)
#             if str(k).startswith('student_') and v:
#                 i = int(str(k).split('_')[-1])
#                 s = Student.objects.get(pk=i)
#                 try:
#                     is_instructor = s.user.is_instructor
#                     instructor_expire = s.user.instructor_expire_date
#                 except (s.DoesNotExist, AttributeError):
#                     is_instructor = False
#                     instructor_expire = None
#
#                 logging.debug(s)
#                 sreg = reg.filter(student=s)
#                 logging.debug(len(sreg))
#                 if len(sreg) == 0:
#                     students.append(s)
#                 else:
#                     messages.add_message(self.request, messages.ERROR,
#                                          'Student is already enrolled')
#                     # message += 'Student is already enrolled'
#                     return self.form_invalid(self.get_form())
#         if len(reg.filter(pay_status='paid')) + len(students) > session.student_limit:
#             messages.add_message(self.request, messages.ERROR,
#                                  'Class is full')
#             # message += 'Class is full'
#             return self.form_invalid(self.get_form())
#         with transaction.atomic():
#             uid = str(uuid.uuid4())
#             self.request.session['idempotency_key'] = uid
#             self.request.session['line_items'] = []
#             self.request.session['payment_db'] = ['joad', 'Registration']
#             self.request.session['action_url'] = reverse_lazy('programs:class_payment')
#             logging.debug(students)
#             for s in students:
#                 cr = Registration(session=session, student=s, pay_status='start', idempotency_key=uid).save()
#                 self.request.session['line_items'].append(
#                     SquareHelper().line_item(f"Joad session starting {str(session.start_date)[:10]} student id: {str(s.id)}",
#                                              1, session.cost))
#                 logging.debug(cr)
#         # This method is called when valid form data has been POSTed.
#         # It should return an HttpResponse.
#         # form.send_email()
#         return HttpResponseRedirect(reverse_lazy('payment:process_payment'))
#         # return super().form_valid(form)
#
#     def post(self, request, *args, **kwargs):
#         logging.debug(self.request.POST)
#         return super().post(request, *args, **kwargs)

class RegistrationView(LoginRequiredMixin, View):
    template_name = 'joad/registration.html'
    form = RegistrationForm

    def get(self, request, session_id=None):
        if session_id:
            session = get_object_or_404(Session, pk=session_id)
            self.form = RegistrationForm(user=request.user, initial={'session': session})
        else:
            self.form = RegistrationForm(user=request.user)
        return render(request, self.template_name, {'form': self.form})

    def has_error(self, request, message):
        messages.add_message(request, messages.ERROR, message)
        return render(request, self.template_name, {'form': self.form})

    def post(self, request, session_id=None):
        logging.debug(request.POST)
        self.form = RegistrationForm(request.user, request.POST)
        if self.form.is_valid():
            students = []
            # message = ""
            logging.debug(self.form.cleaned_data['session'])
            session = self.form.cleaned_data['session']
            if session.state != "open":
                return self.has_error(request, 'Session in wrong state')

            reg = Registration.objects.filter(session=session).exclude(
                pay_status="refunded").exclude(pay_status='canceled')
            logging.debug(len(reg.filter(pay_status='paid')))

            for k, v in self.form.cleaned_data.items():
                logging.debug(k)
                if str(k).startswith('student_') and v:
                    i = int(str(k).split('_')[-1])
                    s = Student.objects.get(pk=i)
                    try:
                        is_instructor = s.user.is_instructor
                        instructor_expire = s.user.instructor_expire_date
                    except (s.DoesNotExist, AttributeError):
                        is_instructor = False
                        instructor_expire = None

                    logging.debug(s)
                    sreg = reg.filter(student=s)
                    logging.debug(len(sreg))
                    if len(sreg) == 0:
                        students.append(s)
                    else:
                        return self.has_error(request, 'Student is already enrolled')

            if len(reg.filter(pay_status='paid')) + len(students) > session.student_limit:
                return self.has_error(request, 'Class is full')

            with transaction.atomic():
                uid = str(uuid.uuid4())
                request.session['idempotency_key'] = uid
                request.session['line_items'] = []
                request.session['payment_db'] = ['joad', 'Registration']
                request.session['action_url'] = reverse('programs:class_payment')
                logging.debug(students)
                for s in students:
                    cr = Registration(session=session, student=s, pay_status='start', idempotency_key=uid).save()
                    request.session['line_items'].append(
                        SquareHelper().line_item(f"Joad session starting {str(session.start_date)[:10]} student id: {str(s.id)}",
                                                 1, session.cost))
                    logging.debug(cr)
            # This method is called when valid form data has been POSTed.
            # It should return an HttpResponse.
            # form.send_email()
            return HttpResponseRedirect(reverse('payment:process_payment'))
        else:
            logging.debug(self.form.errors)
            return render(request, self.template_name, {'form': self.form})
