from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy

from ..models import Session
from ..forms import SessionForm

import logging
logger = logging.getLogger(__name__)


class SessionFormView(UserPassesTestMixin, FormView):
    template_name = 'joad/session.html'
    form_class = SessionForm
    success_url = reverse_lazy('joad:session')
    session = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        logging.debug(kwargs)
        logging.debug(self.session)
        if self.session is not None:
            kwargs['instance'] = self.session
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.session is not None:
            context['session_id'] = self.session.id
        else:
            context['session_id'] = None
        return context

    def form_valid(self, form):
        logging.debug('here')
        f = form.save()
        if self.session:
            return JsonResponse({'session_id': f.id, 'success': True})
        else:
            logging.debug(form.cleaned_data)
            self.success_url = reverse_lazy('joad:session', kwargs={'session_id': f.id})
            return super().form_valid(form)

    def test_func(self):
        if self.kwargs.get('session_id', None) is not None:
            self.session = get_object_or_404(Session, pk=self.kwargs['session_id'])
        return self.request.user.is_board
