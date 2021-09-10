import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic.base import View
from django.utils import timezone

from ..forms import BusinessForm, BusinessUpdateForm
from ..models import Business, BusinessUpdate

logger = logging.getLogger(__name__)


class BusinessView(LoginRequiredMixin, View):
    def get(self, request, business_id=None):
        if business_id:
            report = Business.objects.get(pk=business_id)
            form = BusinessForm(instance=report)
        else:
            form = BusinessForm()
        b = {'form': form, 'id': business_id}
        return render(request, 'minutes/forms/business_form.html', {'business': b})

    def post(self, request, business_id=None):
        logging.debug(request.POST)
        resolved = False
        if business_id:
            report = Business.objects.get(pk=business_id)
            form = BusinessForm(request.POST, instance=report)
        else:
            form = BusinessForm(request.POST)

        if form.is_valid():
            logging.debug(form.cleaned_data)
            report = form.save()
            if form.cleaned_data.get('resolved_bool', False) and report.resolved is None:
                report.resolved = timezone.now()
                resolved = True
            elif not form.cleaned_data.get('resolved_bool', False) and report.resolved:
                report.resolved = None
                resolved = False

            report.save()
            business_id = report.id
            success = True
        else:  # pragma: no cover
            logging.error(form.errors)
            success = False
        return JsonResponse({'business_id': business_id, 'success': success, 'resolved': resolved})


class BusinessUpdateView(LoginRequiredMixin, View):
    def get(self, request, update_id=None):
        logging.debug(request.GET)
        if update_id:
            report = BusinessUpdate.objects.get(pk=update_id)
            form = BusinessUpdateForm(instance=report)
        else:
            form = BusinessUpdateForm()
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
