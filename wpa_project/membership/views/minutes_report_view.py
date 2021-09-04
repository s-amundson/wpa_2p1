import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic.base import View

from ..forms import MinutesReportForm
from ..models import MinutesReport


logger = logging.getLogger(__name__)


class MinutesReportView(LoginRequiredMixin, View):
    def get(self, request, report_id=None):
        logging.debug(request.GET)
        if report_id:
            report = MinutesReport.objects.get(pk=report_id)
            form = MinutesReportForm(instance=report)
        else:
            form = MinutesReportForm()
        r = {'form': form, 'id': report_id}
        return render(request, 'membership/forms/minutes_report_form.html', {'report': r})

    def post(self, request, report_id=None):
        logging.debug(request.POST)
        if report_id:
            report = MinutesReport.objects.get(pk=report_id)
            form = MinutesReportForm(request.POST, instance=report)
        else:
            form = MinutesReportForm(request.POST)

        if form.is_valid():
            logging.debug(form.cleaned_data)
            report = form.save()
            report_id = report.id
            success = True
        else:
            logging.error(form.errors)
            success = False
        return JsonResponse({'report_id': report_id, 'success': success})
