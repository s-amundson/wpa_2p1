import logging

from django.db.models import Q

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.forms import modelformset_factory

from src.mixin import MemberMixin
from ..forms import MinutesForm, ReportForm2, ReportFormset
from ..models import Business, Minutes, Report

logger = logging.getLogger(__name__)


class MinutesView(MemberMixin, FormView):
    template_name = 'minutes/minutes.html'
    form_class = MinutesForm
    success_url = reverse_lazy('registration:index')
    minutes = None
    owners = ['president', 'vice', 'secretary', 'treasure', 'webmaster']

    def dispatch(self, request, *args, **kwargs):
        dispatch = super().dispatch(request, *args, **kwargs)
        if 'minutes' not in self.kwargs:
            if not self.request.user.is_authenticated:
                return self.handle_no_permission()
            if not self.request.user.is_board:
                return self.handle_no_permission()
        return dispatch

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.warning(self.minutes)
        if self.minutes is not None:
            ob = Business.objects.filter(Q(resolved=None, added_date__date__lt=self.minutes.meeting_date) |
                                         Q(resolved__date__gte=self.minutes.meeting_date, added_date__lt=self.minutes.meeting_date))
            nb = Business.objects.filter(minutes=self.minutes)
            logger.warning(nb)
        else:
            ob = nb = Business.objects.none()

        context['old_businesses'] = ob.order_by('added_date', 'id')

        context['new_business'] = nb.order_by('id')
        context['minutes'] = self.minutes
        context['minutes_edit'] = self.minutes is not None and self.minutes.end_time is None

        for owner in self.owners:
            context[f'{owner}_formset'] = self.get_formset(owner)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'minutes' in self.kwargs:
            kwargs['instance'] = self.minutes = get_object_or_404(Minutes, pk=self.kwargs.get('minutes'))
        return kwargs

    def get_formset(self, owner, **kwargs):
        if self.minutes is not None:
            queryset = self.minutes.report_set.filter(owner=owner)
        else:
            queryset = Report.objects.none()
        if self.minutes and self.minutes.end_time is None:
            extra = 1
        else:
            extra = 0
        formset = modelformset_factory(Report, formset=ReportFormset, form=ReportForm2, can_delete=False, extra=extra)
        data = None
        if self.request.method.lower() == 'post':
            data = self.request.POST
        formset = formset(
            queryset=queryset,
            initial=[{'minutes': self.minutes, 'owner': owner}],
            data=data, prefix=owner, **kwargs
            )
        return formset

    def form_invalid(self, form):
        logging.debug(form.errors)
        # if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
        #     return JsonResponse({'business_id': self.business_id, 'success': False, 'resolved': False})
        return super().form_invalid(form)

    def form_valid(self, form):
        minutes = form.save()
        self.success_url = reverse_lazy('minutes:minutes', kwargs={'minutes': minutes.id})
        minutes.save()

        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            return JsonResponse({'minutes': minutes.id, 'success': True})
        return super().form_valid(form)
