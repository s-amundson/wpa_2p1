from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone

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
        logger.debug(kwargs)
        logger.debug(self.session)
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
        f = form.save()
        if 'state' in form.initial:
            for c in f.joadclass_set.filter(event__state=form.initial['state'], event__event_date__gte=timezone.now()):
                c.event.state = f.state
                c.event.save()
        if self.session:
            return JsonResponse({'session_id': f.id, 'success': True})
        else:
            logger.debug(form.cleaned_data)
            self.success_url = reverse_lazy('joad:session', kwargs={'session_id': f.id})
            return super().form_valid(form)

    def test_func(self):
        if self.kwargs.get('session_id', None) is not None:
            self.session = get_object_or_404(Session, pk=self.kwargs['session_id'])
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        return False


class SessionListView(LoginRequiredMixin, ListView):
    model = Session
    template_name = 'joad/session_list.html'
    paginate_by = 20

    def get_queryset(self):
        # filter_date = timezone.now().date() - timezone.timedelta.days(60)
        queryset = self.model.objects.filter(start_date__lt=timezone.now()).order_by('-start_date')
        return queryset


class SessionStatusView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        logger.debug(session_id)
        session = get_object_or_404(Session, pk=session_id)
        registrations = session.registration_set.all()
        student_count = 0
        for r in registrations:
            if r.pay_status in ['paid', 'admin']:
                student_count += 1

        logger.debug(student_count)
        context = {'openings': session.student_limit - student_count, 'limit': session.student_limit,
                   'cost': session.cost, 'status': session.state}
        logger.debug(context)
        return render(request, 'joad/session_status.html', context)
