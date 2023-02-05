from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from ..forms import VolunteerEventForm
from ..models import VolunteerEvent

from event.models import Event
from src.mixin import BoardMixin

import logging
logger = logging.getLogger(__name__)


class VolunteerEventListView(LoginRequiredMixin, ListView):
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
        sid = self.kwargs.get("event_id", None)
        if sid is not None:
            self.volunteer_event = get_object_or_404(VolunteerEvent, pk=sid)
            form = self.form_class(instance=self.volunteer_event, **self.get_form_kwargs())
        else:
            form = self.form_class(**self.get_form_kwargs())
        return form

    def form_invalid(self, form):
        logger.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.debug(form.cleaned_data)
        event = form.save()
        logger.warning(event)
        if event.event is None:
            event.event = Event.objects.create(
                event_date=form.cleaned_data['event_date'],
                state=form.cleaned_data['state'],
                type='joad event'
            )
        else:
            event.event.event_date = form.cleaned_data['event_date']
            event.event.state = form.cleaned_data['state']
            event.event.save()
        event.save()
        return super().form_valid(form)
