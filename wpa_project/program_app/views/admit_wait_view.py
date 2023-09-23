from django.contrib.auth.mixins import UserPassesTestMixin
from django.forms import modelformset_factory
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from ..forms import AdmitWaitForm
from ..tasks import charge_group
from event.forms import RegistrationForm
from event.models import Event, Registration
from student_app.models import StudentFamily, Student

import logging
logger = logging.getLogger(__name__)


class AdmitWaitView(UserPassesTestMixin, FormView):
    template_name = 'program_app/admit_wait.html'
    form_class = RegistrationForm
    event = None
    model = Registration
    success_url = reverse_lazy('payment:make_payment')
    form = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formset = None
        self.student_family = None
        self.formset_students = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['formset'] = self.formset
        context['event_id'] = self.event.id
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['event_queryset'] = Event.objects.filter(pk=self.event.id)
        self.formset_students = Student.objects.filter(registration__event=self.event,
                                                       registration__pay_status__startswith='wait')
        if self.student_family:
            self.formset_students = self.formset_students.filter(student_family=self.student_family)
        logger.warning(self.formset_students)
        kwargs['students'] = self.formset_students
        kwargs['event_type'] = ''
        kwargs['initial']['event'] = self.event.id
        self.get_formset()
        return kwargs

    def get_formset(self, **kwargs):
        data = None
        if self.request.method.lower() == 'post':
            data = self.request.POST
        logger.warning(self.event.registration_set.filter(pay_status__startswith='wait'))
        self.formset = modelformset_factory(Registration, form=AdmitWaitForm, can_delete=False, extra=0)

        event = None
        if 'event' in kwargs:
            event = kwargs.pop('event')
        if 'event' in self.kwargs:
            event = get_object_or_404(Event, pk=self.kwargs.get('event'))

        initial = []
        for student in self.formset_students:
            initial.append({'student': student, 'event': event, 'comment': None})

        self.formset = self.formset(
            queryset=Registration.objects.filter(event=self.event, pay_status__startswith='wait',
                                                 student__in=self.formset_students),
            initial=initial, data=data, **kwargs
            )

    def form_invalid(self, form):  # pragma: no cover
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        reg_list = []
        self.get_formset(event=form.cleaned_data['event'])
        if self.formset.is_valid():
            for f in self.formset:
                logger.warning(f.cleaned_data)
                if f.cleaned_data['admit']:
                    reg_list.append(f.cleaned_data['id'].id)
                    r = f.save()
                    r.pay_status = 'wait processing'
                    r.save()
            if len(reg_list):
                charge_group.delay(reg_list)
                return super().form_valid(form)
        else:  # pragma: no cover
            logger.warning(self.formset.errors)

    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            if self.kwargs.get('event'):
                self.event = get_object_or_404(Event, pk=self.kwargs.get('event'))
                self.success_url = reverse_lazy('programs:admit_wait', kwargs={'event': self.event.id})
            if self.kwargs.get('family_id'):
                self.student_family = get_object_or_404(StudentFamily, pk=self.kwargs.get('family_id'))
        return self.event is not None
