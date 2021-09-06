import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.generic.base import View
from django.utils import timezone
from ..forms import MinutesForm, BusinessForm, BusinessUpdateForm, ReportForm
from ..models import Business, Minutes

logger = logging.getLogger(__name__)


class MinutesFormView(LoginRequiredMixin, View):
    def business_list(self, business, old):
        bl = []
        for b in business:
            logging.debug(b.id)
            update_list =[]
            for update in b.businessupdate_set.all():
                o = timezone.localtime(timezone.now()).date() > update.update_date
                update_list.append({'form': BusinessUpdateForm(instance=update, old=o), 'id': update.id})
            bl.append({'form': BusinessForm(instance=b, old=old), 'id': b.id, 'updates': update_list})
        return bl

    def get(self, request, minutes_id=None):
        if not request.user.is_board:
            return HttpResponseForbidden()
        reports = {}

        owners = ['president', 'vice', 'secretary', 'treasure']
        if minutes_id:
            minutes = Minutes.objects.get(pk=minutes_id)
            form = MinutesForm(instance=minutes, edit=request.user.is_board)
            for owner in owners:
                reports[owner] = self.report_forms(minutes, owner, request.user.is_board)
            ob = Business.objects.filter(Q(resolved=None, added_date__lt=minutes.meeting_date) |
                                            Q(resolved__gte=minutes.meeting_date, added_date__lt=minutes.meeting_date))
            nb = Business.objects.filter(Q(resolved=None, added_date=minutes.meeting_date) |
                                            Q(resolved__gte=minutes.meeting_date, added_date=minutes.meeting_date))
            logging.debug(ob)

        else:
            form = MinutesForm(edit=request.user.is_board)
            for owner in owners:
                reports[owner] = []

            ob = Business.objects.filter(resolved__lt=timezone.now())
            nb = []

        old_business = self.business_list(ob, True)
        new_business = self.business_list(nb, False)

        context = {'form': form, 'minutes_id': minutes_id, 'reports': reports, 'old_business': old_business,
                   'new_business': new_business}

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
            if form.cleaned_data.get('start_time', None) is None:
                minutes = form.save(commit=False)
                minutes.start_time = timezone.now()
                minutes.save()
            else:
                minutes = form.save()
            return HttpResponseRedirect(reverse('minutes:minutes_form', kwargs={'minutes_id': minutes.id}))
        else:  # pragma: no cover
            logging.debug(form.errors)
            return render(request, 'minutes/minutes_form.html', {'form': form})

    def report_forms(self, minutes, owner, is_board):
        forms = []
        for report in minutes.report_set.filter(owner=owner):
            forms.append({'form': ReportForm(instance=report, edit=is_board), 'id': report.id})
        return forms
