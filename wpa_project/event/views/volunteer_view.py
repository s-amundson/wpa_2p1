from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from ..forms import AwardForm, VolunteerEventForm, VolunteerRecordForm
from ..models import VolunteerEvent

from event.models import Event, VolunteerAward
from student_app.models import Student, StudentFamily
from src.mixin import BoardMixin

import logging
logger = logging.getLogger(__name__)


class VolunteerAwardListView(ListView):
    template_name = 'event/volunteer_award_list.html'
    paginate_by = 20
    model = VolunteerAward

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-award_date')


class VolunteerAwardView(BoardMixin, FormView):
    template_name = 'event/award_form.html'
    form_class = AwardForm
    success_url = reverse_lazy('events:volunteer_award')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'pk' in self.kwargs:
            kwargs['instance'] = get_object_or_404(VolunteerAward, pk=self.kwargs['pk'])
        logger.warning(kwargs)

        return kwargs

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        # form.draw_award()
        logger.warning(form.cleaned_data)
        award = form.save()
        self.success_url = reverse_lazy('events:volunteer_award', kwargs={'pk': award.id})
        return super().form_valid(form)


class VolunteerEventListView(ListView):
    template_name = 'event/volunteer_event_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['past'] = self.kwargs.get('past', False)
        return context

    def get_queryset(self):

        if self.kwargs.get('past', False):
            queryset = VolunteerEvent.objects.filter(
                event__event_date__lte=timezone.localtime(timezone.now()).date()).order_by('-event__event_date')
        else:
            queryset = VolunteerEvent.objects.filter(
                event__event_date__gte=timezone.localtime(timezone.now()).date()).order_by('event__event_date')
        return queryset


class VolunteerEventView(BoardMixin, FormView):
    template_name = 'student_app/form_as_p.html'
    form_class = VolunteerEventForm
    success_url = reverse_lazy('events:volunteer_event_list')
    volunteer_event = None

    def get_form(self):
        eid = self.kwargs.get("event", None)
        if eid is not None:
            event = get_object_or_404(Event, pk=eid)
            self.volunteer_event = event.volunteerevent_set.last()
            form = self.form_class(instance=self.volunteer_event, **self.get_form_kwargs())
        else:
            form = self.form_class(**self.get_form_kwargs())
        return form

    def form_invalid(self, form):  # pragma: no cover
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        v_event = form.save()
        if self.volunteer_event:
            self.volunteer_event.event.event_date = form.cleaned_data['event_date']
            self.volunteer_event.event.state = form.cleaned_data['state']
            self.volunteer_event.event.save()
        else:
            v_event.event = Event.objects.create(
                event_date=form.cleaned_data['event_date'],
                state=form.cleaned_data['state'],
                type='work'
            )
        v_event.save()
        logger.warning(f'v_event: {v_event.id} {v_event.description}, event: {v_event.event.id}')
        return super().form_valid(form)


class VolunteerRecordView(BoardMixin, FormView):
    template_name = 'student_app/form_as_p.html'
    form_class = VolunteerRecordForm
    success_url = reverse_lazy('events:volunteer_event_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        logger.warning(self.request.GET)
        if 'student' in self.request.GET:
            logger.warning(self.request.GET['student'])
            kwargs['student'] = get_object_or_404(Student, pk=self.request.GET['student'])
        if 'student_family' in self.request.GET:
            kwargs['student_family'] = get_object_or_404(StudentFamily, pk=self.request.GET['student_family'])
        logger.warning(kwargs)
        return kwargs

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        form.save()
        return super().form_valid(form)
