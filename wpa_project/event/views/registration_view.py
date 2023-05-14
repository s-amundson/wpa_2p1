from django.apps import apps
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid

from ..forms import RegistrationForm
from ..models import Event, Registration
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
        self.event_queryset = Event.objects.filter(
                event_date__gt=timezone.now() - timezone.timedelta(hours=6),
                type=self.event_type
            ).order_by('event_date')

    def get_form_kwargs(self):
        if self.request.user.is_board and 'family_id' in self.kwargs:
            self.student_family = get_object_or_404(StudentFamily, pk=self.kwargs.get('family_id', None))
        if not self.request.user.is_staff:
            self.event_queryset = self.event_queryset.filter(state__in=['open', 'wait'])
        kwargs = super().get_form_kwargs()
        if self.kwargs.get('event', None) is not None:
            kwargs['initial']['event'] = self.kwargs.get('event')
        kwargs['event_queryset'] = self.event_queryset
        kwargs['students'] = self.student_family.student_set.all()
        kwargs['event_type'] = self.event_type
        return kwargs

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def has_error(self, form, message):
        messages.add_message(self.request, messages.ERROR, message)
        logger.warning(message)
        return self.form_invalid(form)


class RegistrationView(RegistrationSuperView):
    event_type = 'work'

    def form_valid(self, form):
        self.form = form
        students = []
        event = form.cleaned_data['event']
        volunteer_event = event.volunteerevent_set.last()
        reg = event.registration_set.exclude(pay_status='canceled')

        for k, v in form.cleaned_data.items():
            logger.debug(k)
            if str(k).startswith('student_') and v:
                i = int(str(k).split('_')[-1])
                s = Student.objects.get(pk=i)

                sreg = reg.filter(student=s)
                if len(sreg) == 0:
                    students.append(s)
                else:
                    return self.has_error(form, 'Student is already enrolled')

        if len(students) == 0:
            return self.has_error(form, 'Invalid student selected')
        else:

            if volunteer_event.volunteer_limit >= len(reg) + len(students):
                ik = uuid.uuid4()
                for s in students:
                    Registration.objects.create(
                        event=event,
                        idempotency_key=ik,
                        pay_status='paid',
                        student=s,
                        user=self.request.user,
                        volunteer_heavy=form.cleaned_data[f'volunteer_heavy_{s.id}']
                    )
                self.success_url = reverse_lazy('registration:profile')
                return super().form_valid(form)
            return self.has_error(form, 'view incomplete')  # pragma: no cover
