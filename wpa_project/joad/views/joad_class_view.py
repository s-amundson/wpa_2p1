from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.urls import reverse_lazy

from ..models import JoadClass, Session
from ..forms import ClassForm
from event.models import Event
from src.mixin import BoardMixin
import logging
logger = logging.getLogger(__name__)


class JoadClassView(BoardMixin, FormView):
    template_name = 'joad/forms/class_form.html'
    form_class = ClassForm
    success_url = reverse_lazy('joad:session')
    form = None
    session = None
    joad_class = None

    def get_form(self):
        return self.form_class(self.session, **self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.joad_class is not None:
            kwargs['instance'] = self.joad_class
        return kwargs

    def form_valid(self, form):
        # don't add a class on a date that already has a class.
        if self.joad_class is None:
            event = Event.objects.create(
                event_date=form.cleaned_data['class_date'],
                # cost_standard=form.cleaned_data['cost'],
                # cost_member=form.cleaned_data['cost'],
                state=form.cleaned_data['state'],
                type='joad class'
            )
        else:
            event = self.joad_class.event
            event.event_date = form.cleaned_data['class_date']
            # event.cost_standard = form.cleaned_data['cost']
            # event.cost_member = form.cleaned_data['cost']
            event.state = form.cleaned_data['state']
            event.save()

        f = form.save()
        f.event = event
        f.save()

        return JsonResponse({'id': f.id, 'class_date': f.event.event_date, 'state': f.event.state, 'success': True})

    def test_func(self):
        is_board = super().test_func()
        if is_board:
            self.session = get_object_or_404(Session, pk=self.kwargs['session_id'])
            if self.kwargs.get('class_id', None) is not None:
                self.joad_class = get_object_or_404(JoadClass, pk=self.kwargs['class_id'])
        return is_board


class ClassListView(LoginRequiredMixin, ListView):
    model = JoadClass
    template_name = 'joad/tables/class_table.html'

    def get_queryset(self):
        sid = self.kwargs.get("session_id", None)
        logger.debug(sid)
        if sid == 0:
            object_list = self.model.objects.filter(session__state="open")
        elif sid is not None:
            object_list = self.model.objects.filter(session_id=sid).order_by('event__event_date')
        else:
            object_list = []

        return object_list

