from django.forms import modelformset_factory
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid

from ..forms import RegistrationForm, RegistrationForm2
from ..models import Event, Registration
from src.mixin import StudentFamilyMixin
from student_app.models import Student, StudentFamily

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
        self.formset = None
        self.formset_students = []
        self.events = Event.objects.none()
        self.students = []
        self.admin_registration = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['admin_registration'] = self.admin_registration
        context['formset'] = self.formset
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_board and 'family_id' in self.kwargs:
            self.student_family = get_object_or_404(StudentFamily, pk=self.kwargs.get('family_id', None))
        if not self.request.user.is_staff:
            self.event_queryset = self.event_queryset.filter(state__in=['open', 'wait'])

        if self.kwargs.get('event', None) is not None:
            kwargs['initial']['event'] = self.kwargs.get('event')
            # self.event = get_object_or_404(Event, pk=self.kwargs.get('event'))
            self.events = self.event_queryset.filter(pk=self.kwargs.get('event'))
            if not self.request.user.is_staff:
                self.event_queryset = self.events
            else:
                self.event_queryset = self.event_queryset.filter(
                    event_date__date=self.events.last().event_date
                )
        kwargs['event_queryset'] = self.event_queryset
        kwargs['students'] = self.formset_students = self.student_family.student_set.all()
        kwargs['event_type'] = self.event_type
        self.get_formset()
        return kwargs

    def get_formset(self, **kwargs):
        data = None
        if self.request.method.lower() == 'post':
            data = self.request.POST
            if self.request.user.is_board:
                self.formset_students = Student.objects.all()
        self.formset = modelformset_factory(Registration, form=RegistrationForm2, can_delete=False,
                                            extra=len(self.formset_students))

        event = None
        if 'event' in kwargs:
            event = kwargs.pop('event')
        if 'event' in self.kwargs:
            event = get_object_or_404(Event, pk=self.kwargs.get('event'))

        initial = []
        for student in self.formset_students:
            initial.append({'student': student, 'event': event, 'comment': None})

        self.formset = self.formset(
            form_kwargs={
                'students': self.formset_students,
                'is_staff': self.request.user.is_staff,
                'event_type': self.event_type
            },
            queryset=Registration.objects.none(),
            initial=initial, data=data, **kwargs
            )

    def form_invalid(self, form):
        logger.warning(self.request.POST)
        logger.warning(form.errors)
        return super().form_invalid(form)

    def has_error(self, form, message):
        messages.add_message(self.request, messages.ERROR, message)
        logger.warning(message)
        return self.form_invalid(form)

    def process_formset(self):
        self.get_formset(event=self.form.cleaned_data['event'])
        self.events = self.form.cleaned_data['event']
        logger.warning(self.form.cleaned_data['event'])
        # reg = self.event.registration_set.exclude(pay_status__in=['canceled', "refunded", 'refund', 'refund donated'])
        reg = Registration.objects.filter(event__in=self.form.cleaned_data['event']).exclude(
            pay_status__in=['canceled', "refunded", 'refund', 'refund donated'])
        if self.formset.is_valid():
            try:
                for event in self.events:
                    for f in self.formset:
                        if f.cleaned_data['register']:
                            if reg.filter(student=f.cleaned_data['student']):
                                # return {'success': False, 'error': 'Student is already enrolled'}
                                raise Exception('Student is already enrolled')
                            self.students.append(f.cleaned_data['student'].id)
                    # make self.students a queryset.
                self.students = self.student_family.student_set.filter(id__in=self.students)
            except Exception as e:
                return {'success': False, 'error': e}
            return {'success': True, 'error': ''}
        else:
            logger.warning(self.formset.errors)
            logger.warning(self.formset.non_form_errors())
        return {'success': False, 'error': 'Error with form'}


class RegistrationView(RegistrationSuperView):
    event_type = 'work'

    def form_valid(self, form):
        self.form = form
        logger.warning(form.cleaned_data)
        if self.request.user.is_board:
            self.student_family = get_object_or_404(StudentFamily, pk=form.cleaned_data['student_family'])
        processed_formset = self.process_formset()
        if not processed_formset['success']:
            return self.has_error(self.form, processed_formset['error'])

        ik = uuid.uuid4()
        for f in self.formset:
            for event in self.events:
                logger.warning(event)
                if f.cleaned_data['register']:
                    logger.warning(f.instance)
                    # f.instance = None
                    new_reg = Registration.objects.create(
                        event=event,
                        student=f.cleaned_data['student'],
                        pay_status='paid',
                        idempotency_key=ik,
                        user=self.request.user,
                        comment=f.cleaned_data.get('comment', None)
                    )

                    logger.warning(new_reg)

            self.success_url = reverse_lazy('registration:profile')
        return super().form_valid(form)
        # else:
        #     logger.warning(self.formset.errors)
        # return self.has_error(form, 'Error with form')  # pragma: no cover
