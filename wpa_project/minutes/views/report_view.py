import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic.base import View

from ..forms import ReportForm
from ..models import Report


logger = logging.getLogger(__name__)


class ReportView(LoginRequiredMixin, View):
    def get(self, request, report_id=None):
        logging.debug(request.GET)
        if report_id:
            report = Report.objects.get(pk=report_id)
            form = ReportForm(instance=report)
        else:
            form = ReportForm()
        r = {'form': form, 'id': report_id}
        return render(request, 'minutes/forms/report_form.html', {'report': r})

    def post(self, request, report_id=None):
        logging.debug(request.POST)
        if report_id:
            report = Report.objects.get(pk=report_id)
            form = ReportForm(request.POST, instance=report)
        else:
            form = ReportForm(request.POST)

        if form.is_valid():
            logging.debug(form.cleaned_data)
            report = form.save()
            report_id = report.id
            success = True
        else:  # pragma: no cover
            logging.error(form.errors)
            success = False
        return JsonResponse({'report_id': report_id, 'success': success})
