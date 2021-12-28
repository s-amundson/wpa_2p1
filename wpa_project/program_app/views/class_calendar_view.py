import logging

from django.views.generic.base import View
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from ..src import Calendar
logger = logging.getLogger(__name__)


class ClassCalendarView(View):
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
        cal = Calendar(d.year, month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = mark_safe(cal.formatmonth(withyear=True))
        return HttpResponse(html_cal)
