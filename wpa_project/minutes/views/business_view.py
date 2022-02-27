import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic.base import View
from django.utils import timezone
from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages

from ..forms import BusinessForm, BusinessUpdateForm
from ..models import Business, BusinessUpdate

logger = logging.getLogger(__name__)


class BusinessView(UserPassesTestMixin, FormView):
    template_name = 'minutes/forms/business_form.html'
    form_class = BusinessForm
    success_url = reverse_lazy('registration:index')
    business_id = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return {'business': {'form': context['form'], 'id': self.business_id}}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.business_id is not None:
            kwargs['instance'] = Business.objects.get(pk=self.business_id)
        kwargs['report'] = self.request.GET.get('report_index', None)
        return kwargs

    def form_invalid(self, form):
        logging.debug(form.errors)
        return JsonResponse({'business_id': self.business_id, 'success': False, 'resolved': False})

    def form_valid(self, form):
        report = form.save()
        resolved = False
        if form.cleaned_data.get('resolved_bool', False) and report.resolved is None:
            report.resolved = timezone.now()
            resolved = True
        elif not form.cleaned_data.get('resolved_bool', False) and report.resolved:
            report.resolved = None
            resolved = False

        report.save()
        self.business_id = report.id
        return JsonResponse({'business_id': self.business_id, 'success': True, 'resolved': resolved})

    def test_func(self):
        logging.debug(self.request.GET)
        logging.debug(self.kwargs)
        self.business_id = self.kwargs.get('business_id', None)
        if self.request.method == 'GET':
            return self.request.user.is_member
        return self.request.user.is_board


class BusinessUpdateView(LoginRequiredMixin, View):
    def get(self, request, update_id=None):
        logging.debug(request.GET)
        if update_id:
            report = BusinessUpdate.objects.get(pk=update_id)
            form = BusinessUpdateForm(instance=report, report=request.GET.get('report_index', None))
        else:
            form = BusinessUpdateForm(report=request.GET.get('report_index', None))
        b = {'form': form, 'id': update_id}
        return render(request, 'minutes/forms/business_update_form.html', {'update': b})

    def post(self, request, update_id=None):
        logging.debug(request.POST)
        if update_id:
            report = BusinessUpdate.objects.get(pk=update_id)
            form = BusinessUpdateForm(request.POST, instance=report)
        else:
            form = BusinessUpdateForm(request.POST)

        if form.is_valid():
            logging.debug(form.cleaned_data)
            report = form.save()
            update_id = report.id
            success = True
        else:  # pragma: no cover
            logging.error(form.errors)
            success = False
        return JsonResponse({'update_id': update_id, 'success': success})
