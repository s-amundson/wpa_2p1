from django.utils import timezone
from calendar import HTMLCalendar

from ..models import BeginnerClass
import logging
logger = logging.getLogger(__name__)


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, dark=False):
        self.year = year
        self.month = month
        self.events = BeginnerClass.objects.filter(class_date__gt=timezone.now(),
                                                   class_date__year=self.year,
                                                   class_date__month=self.month,
                                                   state='open')
        self.dark = dark
        super(Calendar, self).__init__()
        self.setfirstweekday(6)

    # formats a day as a td
    # filter events by day
    def formatday(self, day):
        events_per_day = self.events.filter(class_date__day=day)
        data = ''

        for event in events_per_day:
            logging.debug(event.class_type)
            btn_color = 'btn-primary'
            if event.class_type == 'combined':
                btn_color = 'btn-info'
            elif event.class_type == 'returnee':
                btn_color = 'btn-secondary'
            cd = timezone.localtime(event.class_date)
            data += f'<li><button class="btn {btn_color} bc-btn m-1" type="button" bc_id="{event.id}">'
            data += f'{event.class_type.capitalize()} {cd.strftime("%I:%M %p")}</button></li>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {data} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        if self.dark:
            bg = 'table-dark'
        else:
            bg = ''
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar table table-bordered {bg}">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week)}\n'
        return cal
