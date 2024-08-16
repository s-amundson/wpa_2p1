import logging
from django.views.generic.base import TemplateView
from django.utils import timezone
from django.utils.safestring import mark_safe

from facebook.views import PostList
from ..models import BeginnerClass
from ..src import Calendar
logger = logging.getLogger(__name__)


class CalendarView(TemplateView):
    template_name = "program_app/calendar.html"

    def coerce_month(self, year, month):
        if month > 12:
            while month > 12:
                year += 1
                month = month - 12
        if month <= 0:
            while month <= 0:
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
        beginner_class = BeginnerClass.objects.filter(event__event_date__gt=timezone.now())
            # class_date__gt=timezone.now(), state='open').order_by('class_date')
        beginner_wait = beginner_class.filter(class_type='beginner', event__state='wait').order_by('event__event_date')
        returnee_class = beginner_class.filter(class_type='returnee', event__state='open').order_by('event__event_date')
        returnee_wait = beginner_class.filter(class_type='returnee', event__state='wait').order_by('event__event_date')
        beginner_class = beginner_class.filter(class_type='beginner', event__state='open').order_by('event__event_date')
        if beginner_class:
            context['beginner_class'] = beginner_class.first()
        else:
            context['beginner_class'] = None
        if beginner_wait:
            context['beginner_wait'] = beginner_wait.first()
        else:
            context['beginner_wait'] = None
        if returnee_class:
            context['returnee_class'] = returnee_class.first()
        else:
            context['returnee_class'] = None
        if returnee_wait:
            context['returnee_wait'] = returnee_wait.first()
        else:
            context['returnee_wait'] = None

        # Instantiate our calendar class with selected year and month
        dark = False
        if self.request.user.is_authenticated:
            dark = self.request.user.dark_theme
        cal = Calendar(year, month, dark, self.request.user.is_staff)

        # Call the formatmonth method, which returns our calendar as a table
        context['html_cal'] = mark_safe(cal.formatmonth(withyear=True))

        return context


class EventCalendarView(PostList):
    template_name = 'program_app/google_calendar.html'
