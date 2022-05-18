import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.utils import timezone
from ..forms import MinutesForm, BusinessForm, BusinessUpdateForm, DecisionForm, ReportForm
from ..models import Business, Decision, Minutes

logger = logging.getLogger(__name__)


class MinutesFormView(LoginRequiredMixin, View):
    report_index = 0

    def business_list(self, business, old):
        bl = []
        for b in business:
            update_list = []
            for update in b.businessupdate_set.all():
                logging.debug(update.update_date)
                logging.debug(update.update_date.date())
                o = timezone.now().date() > update.update_date.date()
                update_list.append({'form': BusinessUpdateForm(instance=update, old=o, report=self.report_index),
                                    'id': update.id})
                self.report_index += 1
            bl.append({'form': BusinessForm(instance=b, old=old, report=self.report_index), 'id': b.id, 'updates': update_list})
            self.report_index += 1
        return bl

    def get(self, request, minutes_id=None):
        logging.debug(request.POST)
        logging.debug(request.user.is_member)
        if not request.user.is_member:
            return HttpResponseForbidden()
        reports = {}

        owners = ['president', 'vice', 'secretary', 'treasure']
        if minutes_id:
            minutes = Minutes.objects.get(pk=minutes_id)
            form = MinutesForm(instance=minutes, edit=request.user.is_board)
            for owner in owners:
                reports[owner] = self.report_forms(minutes, owner, request.user.is_board)
            ob = Business.objects.filter(Q(resolved=None, added_date__date__lt=minutes.meeting_date) |
                                         Q(resolved__date__gte=minutes.meeting_date, added_date__lt=minutes.meeting_date))
            ob = ob.order_by('added_date', 'id')
            logging.debug(ob)
            nb = Business.objects.filter(Q(resolved=None, added_date__date=minutes.meeting_date) |
                                         Q(resolved__date__gte=minutes.meeting_date, added_date__date=minutes.meeting_date))
            nb = nb.order_by('id')
            decisions_query = Decision.objects.filter(decision_date__date=minutes.meeting_date.date()).order_by('id')
            logging.debug(decisions_query)

        else:
            form = MinutesForm(edit=request.user.is_board)
            for owner in owners:
                reports[owner] = []

            ob = Business.objects.filter(resolved__lt=timezone.now()).order_by('added_date', 'id')
            nb = []
            decisions_query = Decision.objects.filter(decision_date=timezone.now()).order_by('id')

        old_business = self.business_list(ob, True)
        new_business = self.business_list(nb, False)
        decisions = []
        for decision in decisions_query:
            decisions.append({'form': DecisionForm(instance=decision, report_index=self.report_index), 'id': decision.id})
            self.report_index += 1

        context = {'form': form, 'minutes_id': minutes_id, 'reports': reports, 'old_business': old_business,
                   'new_business': new_business, 'decisions': decisions, 'report_index': self.report_index}

        return render(request, 'minutes/minutes_form.html', context)

    def post(self, request, minutes_id=None):
        logging.debug(request.POST)
        if not request.user.is_board:
            return HttpResponseForbidden()
        if minutes_id:
            minutes = Minutes.objects.get(pk=minutes_id)
            form = MinutesForm(request.POST, instance=minutes)
        else:
            form = MinutesForm(request.POST)

        if form.is_valid():
            logging.debug(form.cleaned_data)
            if minutes_id is None:
                minutes = form.save(commit=False)
                minutes.meeting_date = timezone.now()
                minutes.save()
            else:
                minutes = form.save()
            if request.POST.get('update', False):
                logging.debug('json response')
                return JsonResponse({'minutes_id': minutes.id, 'success': True})
            return HttpResponseRedirect(reverse('minutes:minutes_form', kwargs={'minutes_id': minutes.id}))
        else:  # pragma: no cover
            logging.debug(form.errors)
            if request.POST.get('update', False):
                logging.debug('json response')
                return JsonResponse({'minutes_id': minutes_id, 'success': False})
            return render(request, 'minutes/minutes_form.html', {'form': form})

    def report_forms(self, minutes, owner, is_board):
        forms = []
        for report in minutes.report_set.filter(owner=owner):
            forms.append({'form': ReportForm(instance=report, edit=is_board, report_index=self.report_index),
                          'id': report.id})
            self.report_index += 1
        return forms
