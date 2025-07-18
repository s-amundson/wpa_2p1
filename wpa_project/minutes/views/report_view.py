import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic.base import View

from ..forms import ReportForm
from ..models import Report


logger = logging.getLogger(__name__)


class ReportView(LoginRequiredMixin, View):
    def get(self, request, report_id=None):
        if not request.user.has_perm('student_app.members'):
            return HttpResponseForbidden()
        logging.debug(request.GET)
        if report_id:
            report = Report.objects.get(pk=report_id)
            form = ReportForm(instance=report, edit=request.user.has_perm('student_app.board'), report_index=request.GET.get('report_index', None))
        else:
            form = ReportForm(edit=request.user.has_perm('student_app.board'), report_index=request.GET.get('report_index', None))
        r = {'form': form, 'id': report_id}
        logging.debug(r)
        return render(request, 'minutes/forms/report_form.html', {'report': r})

    def post(self, request, report_id=None):
        if not request.user.has_perm('student_app.board'):
            return HttpResponseForbidden()
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
