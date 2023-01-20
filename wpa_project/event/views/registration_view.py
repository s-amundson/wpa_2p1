from django.apps import apps
from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404


from ..forms import RegistrationForm
from ..models import Registration
from src.mixin import StudentFamilyMixin
from student_app.models import Student
StudentFamily = apps.get_model(app_label='student_app', model_name='StudentFamily')

import logging
logger = logging.getLogger(__name__)


class RegistrationSuperView(StudentFamilyMixin, FormView):
    template_name = 'event/registration.html'
    form_class = RegistrationForm
    event_type = 'class'
    model = Registration
    success_url = reverse_lazy('payment:make_payment')
    form = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait = False
        self.has_card = False

    def get_form_kwargs(self):
        if self.request.user.is_board and 'family_id' in self.kwargs:
            self.student_family = get_object_or_404(StudentFamily, pk=self.kwargs.get('family_id', None))
        kwargs = super().get_form_kwargs()
        # logging.warning(self.kwargs)
        if self.kwargs.get('event', None) is not None:
            kwargs['initial']['event'] = self.kwargs.get('event')
        kwargs['event_type'] = self.event_type
        kwargs['students'] = self.student_family.student_set.all()
        return kwargs

    def get_initial(self):
        evt = self.kwargs.get('event', False)
        if evt:
            self.initial = {'volunteer_event': evt}
        return super().get_initial()

    def form_invalid(self, form):
        logging.warning(form.errors)
        return super().form_invalid(form)

    def has_error(self, form, message):
        messages.add_message(self.request, messages.ERROR, message)
        logging.warning(message)
        return self.form_invalid(form)

    def post(self, request, *args, **kwargs):
        logging.warning(self.request.POST)
        return super().post(request, *args, **kwargs)


class RegistrationView(RegistrationSuperView):
    event_type = 'work'

    def form_valid(self, form):
        self.form = form
        students = []
        volunteer_event = form.cleaned_data['volunteer_event']
        reg = volunteer_event.volunteerregistration_set.exclude(canceled=True)
        logging.warning(len(reg))

        for k, v in form.cleaned_data.items():
            logging.debug(k)
            if str(k).startswith('student_') and v:
                i = int(str(k).split('_')[-1])
                s = Student.objects.get(pk=i)

                logging.warning(s)
                logging.warning(len(reg.filter(student__id=i)))
                sreg = reg.filter(student=s)
                logging.warning(len(sreg))
                if len(sreg) == 0:
                    students.append(s)
                else:
                    return self.has_error(form, 'Student is already enrolled')

        if len(students) == 0:
            return self.has_error(form, 'Invalid student selected')
        else:
            if volunteer_event.volunteer_limit >= volunteer_event.volunteerregistration_set.registered_count() + len(students):
                for s in students:
                    Registration.objects.create(
                        event=volunteer_event,
                        student=s,
                        user=self.request.user
                    )
                return super().form_valid(form)
            return self.has_error(form, 'view incomplete')


# class ResumeRegistrationView(LoginRequiredMixin, View):
#     def get(self, request, reg_id=None):
#         registration = get_object_or_404(Registration, pk=reg_id)
#         registrations = Registration.objects.filter(idempotency_key=registration.idempotency_key)
#         logging.debug(registration)
#         self.request.session['idempotency_key'] = str(registration.idempotency_key)
#         self.request.session['line_items'] = []
#         self.request.session['payment_category'] = 'joad'
#
#         for r in registrations:
#             self.request.session['payment_description'] = f'Joad session starting {str(r.session.start_date)[:10]}'
#             self.request.session['line_items'].append(
#                     {'name': f'Joad session starting {str(r.session.start_date)[:10]} student id: {str(r.student.id)}',
#                      'quantity': 1, 'amount_each': r.session.cost})
#         return HttpResponseRedirect(reverse('payment:make_payment'))


# class RegistrationCancelView(RegistrationSuperView):
#     success_url = reverse_lazy('joad:index')

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     if self.request.user.is_board:
    #         students = Student.objects.filter(is_joad=True)
    #     else:
    #         students = self.request.user.student_set.last().student_family.student_set.filter(is_joad=True)
    #     logging.debug(students)
    #     kwargs['students'] = students.filter(registration__in=self.session.registration_set.all())
    #     kwargs['cancel'] = True
    #     logging.debug(kwargs)
    #     return kwargs
    #
    # def form_valid(self, form):
    #     logging.debug(form.cleaned_data)
    #     if form.process_refund(self.request.user):
    #         return super().form_valid(form)
    #     else:
    #         return self.form_invalid(form)
    #
    #
    # def test_func(self):
    #     if super().test_func():
    #         return self.session is not None
    #     return False
