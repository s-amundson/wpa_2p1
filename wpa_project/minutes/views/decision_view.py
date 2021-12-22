import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic.base import View

from ..forms import DecisionForm
from ..models import Decision


logger = logging.getLogger(__name__)


class DecisionView(LoginRequiredMixin, View):
    def get(self, request, decision_id=None):
        if not request.user.is_member:
            return HttpResponseForbidden()
        if decision_id:
            report = Decision.objects.get(pk=decision_id)
            form = DecisionForm(instance=report)
        else:
            form = DecisionForm(edit=request.user.is_board)
        r = {'form': form, 'id': decision_id}
        return render(request, 'minutes/forms/decision_form.html', {'decision': r})

    def post(self, request, decision_id=None):
        if not request.user.is_board:
            return HttpResponseForbidden()
        if decision_id:
            report = Decision.objects.get(pk=decision_id)
            form = DecisionForm(request.POST, instance=report)
        else:
            form = DecisionForm(request.POST)

        if form.is_valid():
            report = form.save()
            decision_id = report.id
            success = True
        else:  # pragma: no cover
            logging.error(form.errors)
            success = False
        return JsonResponse({'decision_id': decision_id, 'success': success})
