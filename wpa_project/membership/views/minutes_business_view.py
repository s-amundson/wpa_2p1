import logging
import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.utils import timezone
from django.utils.datetime_safe import date
from django.contrib import messages
from django.forms import model_to_dict
from ..forms import MinutesBusinessForm, MinutesBusinessUpdateForm
from ..models import MinutesBusiness, MinutesBusinessUpdate


logger = logging.getLogger(__name__)


class MinutesBusinessView(LoginRequiredMixin, View):
    def get(self, request, business_id=None):
        logging.debug(request.GET)
        if business_id:
            report = MinutesBusiness.objects.get(pk=business_id)
            form = MinutesBusinessForm(instance=report)
        else:
            form = MinutesBusinessForm()
        b = {'form': form, 'id': business_id}
        return render(request, 'membership/forms/minutes_business_form.html', {'business': b})

    def post(self, request, business_id=None):
        logging.debug(request.POST)
        resolved = False
        if business_id:
            report = MinutesBusiness.objects.get(pk=business_id)
            form = MinutesBusinessForm(request.POST, instance=report)
        else:
            form = MinutesBusinessForm(request.POST)

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
        else:
            logging.error(form.errors)
            success = False
        return JsonResponse({'business_id': business_id, 'success': success, 'resolved': resolved})


class MinutesBusinessUpdateView(LoginRequiredMixin, View):
    def get(self, request, update_id=None):
        logging.debug(request.GET)
        if update_id:
            report = MinutesBusinessUpdate.objects.get(pk=update_id)
            form = MinutesBusinessUpdateForm(instance=report)
        else:
            form = MinutesBusinessUpdateForm()
        b = {'form': form, 'id': update_id}
        return render(request, 'membership/forms/minutes_business_update_form.html', {'update': b})

    def post(self, request, update_id=None):
        logging.debug(request.POST)
        if update_id:
            report = MinutesBusinessUpdate.objects.get(pk=update_id)
            form = MinutesBusinessUpdateForm(request.POST, instance=report)
        else:
            form = MinutesBusinessUpdateForm(request.POST)

        if form.is_valid():
            logging.debug(form.cleaned_data)
            report = form.save()
            update_id = report.id
            success = True
        else:
            logging.error(form.errors)
            success = False
        return JsonResponse({'update_id': update_id, 'success': success})
