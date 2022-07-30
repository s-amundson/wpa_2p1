import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View
from django.views.generic.base import TemplateView
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from ..src import Calendar
logger = logging.getLogger(__name__)


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = "program_app/calendar.html"

    def coerce_month(self, year, month):
        if month > 12:
            while month > 12:
                year += 1
                month = month - 12
        if month < 0:
            while month < 0:
                year -= 1
                month = month + 12
        return year, month

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # use today's date for the calendar
        d = timezone.localtime(timezone.now()).date()
        year = self.kwargs.get('year', d.year)
        month = self.kwargs.get('month', d.month)
        year, month = self.coerce_month(year, month)
        ny, nm = self.coerce_month(year, month + 1)
        context['next'] = {'year': ny, 'month': nm}
        ly, lm = self.coerce_month(year, month - 1)
        context['previous'] = {'year': ly, 'month': lm}
        context['this_month'] = d.year == year and d.month == month

        # Instantiate our calendar class with selected year and month
        cal = Calendar(year, month, self.request.user.dark_theme, self.request.user.is_staff)

        # Call the formatmonth method, which returns our calendar as a table
        context['html_cal'] = mark_safe(cal.formatmonth(withyear=True))
        return context


class ClassCalendarView(LoginRequiredMixin, View):
    def get(self, request, month=None):
        # use today's date for the calendar
        d = timezone.localtime(timezone.now()).date()
        if month is None:
            month = d.month

        if month > 12:
            while month > 12:
                d = d.replace(year=d.year + 1)
                month = month - 12
        # Instantiate our calendar class with today's year and selected month
        cal = Calendar(d.year, month, request.user.dark_theme, request.user.is_staff)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = mark_safe(cal.formatmonth(withyear=True))
        return HttpResponse(html_cal)
