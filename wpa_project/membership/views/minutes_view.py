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
from ..forms import MinutesForm, MinutesBusinessForm, MinutesReportForm
from ..models import LevelModel, MinutesBusinessModel, MinutesModel, MinutesReportModel


logger = logging.getLogger(__name__)


class MinutesBusinessView(LoginRequiredMixin, View):
    def get(self, request, business_id=None):
        logging.debug(request.GET)
        if business_id:
            report = MinutesBusinessModel.objects.get(pk=business_id)
            form = MinutesBusinessForm(instance=report)
        else:
            form = MinutesBusinessForm()
        b = {'form': form, 'id': business_id}
        return render(request, 'membership/forms/minutes_business_form.html', {'business': b})

    def post(self, request, business_id=None):
        logging.debug(request.POST)
        if business_id:
            report = MinutesBusinessModel.objects.get(pk=business_id)
            form = MinutesBusinessForm(request.POST, instance=report)
        else:
            form = MinutesBusinessForm(request.POST)

        if form.is_valid():
            logging.debug(form.cleaned_data)
            report = form.save()
            business_id = report.id
        else:
            logging.error(form.errors)
        return JsonResponse({'business_id': business_id})
    

class MinutesFormView(LoginRequiredMixin, View):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.table = LevelModel.objects.all()

    def get(self, request, minutes_id=None):
        if not request.user.is_board:
            return HttpResponseForbidden()
        reports = {}

        owners = ['president', 'vice', 'secretary', 'treasure']
        if minutes_id:
            minutes = MinutesModel.objects.get(pk=minutes_id)
            form = MinutesForm(instance=minutes)
            for owner in owners:
                reports[owner] = self.report_forms(minutes, owner)
                
            ob = MinutesBusinessModel.objects.filter(resolved=False, added_date__lt=minutes.meeting_date)
            logging.debug(ob)

        else:
            form = MinutesForm()
            for owner in owners:
                reports[owner] = []

            ob = MinutesBusinessModel.objects.filter(resolved=False)

        old_business = []
        for b in ob:
            old_business.append({'form': MinutesBusinessForm(instance=b), 'id': b.id})
        logging.debug(old_business)
        context = {'form': form, 'minutes_id': minutes_id, 'reports': reports, 'old_business': old_business}
        return render(request, 'membership/minutes_form.html', context)

    def post(self, request, minutes_id=None):
        logging.debug(request.POST)
        if not request.user.is_board:
            return HttpResponseForbidden()
        if minutes_id:
            minutes = MinutesModel.objects.get(pk=minutes_id)
            form = MinutesForm(request.POST, instance=minutes)
        else:
            form = MinutesForm(request.POST)

        if form.is_valid():
            if form.cleaned_data.get('start_time', None) is None:
                minutes = form.save(commit=False)
                minutes.start_time = timezone.localtime.now()
                minutes.save()
            else:
                minutes = form.save()
            return HttpResponseRedirect(reverse('membership:minutes_form', kwargs={'minutes_id': minutes.id}))
        else:
            logging.debug(form.errors)
            return render(request, 'membership/minutes_form.html', {'form': form})

    def report_forms(self, minutes, owner):
        forms = []
        for report in minutes.minutesreportmodel_set.filter(owner=owner):
            forms.append({'form': MinutesReportForm(instance=report), 'id': report.id})
        return forms


class MinutesReportView(LoginRequiredMixin, View):
    def get(self, request, report_id=None):
        logging.debug(request.GET)
        if report_id:
            report = MinutesReportModel.objects.get(pk=report_id)
            form = MinutesReportForm(instance=report)
        else:
            form = MinutesReportForm()
        r = {'form': form, 'id': report_id}
        return render(request, 'membership/forms/minutes_report_form.html', {'report': r})

    def post(self, request, report_id=None):
        logging.debug(request.POST)
        if report_id:
            report = MinutesReportModel.objects.get(pk=report_id)
            form = MinutesReportForm(request.POST, instance=report)
        else:
            form = MinutesReportForm(request.POST)

        if form.is_valid():
            logging.debug(form.cleaned_data)
            report = form.save()
            report_id = report.id
        else:
            logging.error(form.errors)
        return JsonResponse({'report_id': report_id})
