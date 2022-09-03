from django.utils import timezone
from django.urls import reverse
from calendar import HTMLCalendar
from ..models import BeginnerClass
from joad.models import JoadClass, JoadEvent
import logging
logger = logging.getLogger(__name__)


class Calendar(HTMLCalendar):
    class Event:
        def __init__(self, id, class_date, class_type, state, session=None):
            self.id = id
            self.class_date = class_date
            self.class_type = class_type
            self.state = state
            self.session = session

    def __init__(self, year=None, month=None, dark=False, staff=False):
        self.year = year
        self.month = month
        self.events = BeginnerClass.objects.filter(class_date__gt=timezone.now(),
                                                   class_date__year=year,
                                                   class_date__month=month).order_by('class_date')
        if not staff:
            self.events = self.events.exclude(class_type='special')
        self.joad_class_events = JoadClass.objects.filter(class_date__gt=timezone.now(),
                                                          class_date__year=year,
                                                          class_date__month=month).order_by('class_date')
        self.joad_events = JoadEvent.objects.filter(event_date__gt=timezone.now(),
                                                    event_date__year=year,
                                                    event_date__month=month).order_by('event_date')

        self.dark = dark
        self.staff = staff
        super(Calendar, self).__init__()
        self.setfirstweekday(6)

    def insert_event(self, event_list, event):
        for i in range(len(event_list)):
            if event_list[i].class_date > event.class_date:
                event_list.insert(i, event)
                return event_list
        event_list.append(event)
        return event_list

    # formats a day as a td
    # filter events by day
    def formatday(self, day):
        event_list = []
        for event in self.events.filter(class_date__day=day):
            event_list.append(self.Event(event.id, event.class_date, event.class_type, event.state))
        for event in self.joad_class_events.filter(class_date__day=day):
            event_list = self.insert_event(event_list, self.Event(event.id, event.class_date, 'JOAD Class',
                                                                  event.state, event.session))
        for event in self.joad_events.filter(event_date__day=day):
            event_list = self.insert_event(event_list, self.Event(event.id, event.event_date, event.event_type,
                                                                  event.state))

        data = ''

        for event in event_list:
            cd = timezone.localtime(event.class_date)
            if event.class_type == 'JOAD Class':
                url = reverse('joad:registration', kwargs={'session_id': event.session.id})
                data += f'<a href="{url}" role="button"'

                if event.session.state not in ['open']:
                    data += f' class="btn btn-warning disabled m-1" disabled aria-disabled="true"> ' \
                            f'JOAD Class {cd.strftime("%I:%M %p")} CLOSED</a>'
                else:
                    data += f'  class="btn btn-warning m-1"> JOAD Class {cd.strftime("%I:%M %p")}</a>'

            elif event.class_type == 'joad_indoor':
                url = reverse('joad:event_registration', kwargs={'event_id': event.id})
                data += f'<a href="{url}" role="button"'
                if event.state not in ['open']:
                    data += f' class="btn btn-warning disabled m-1" disabled aria-disabled="true"> ' \
                            f'JOAD Pin Shoot {cd.strftime("%I:%M %p")} CLOSED</a>'
                else:
                    data += f'  class="btn btn-warning m-1"> JOAD Pin Shoot {cd.strftime("%I:%M %p")}</a>'

            else:  # elif event.class_type in ['beginner', 'combined', 'returnee']:
                btn_color = 'btn-primary'
                if event.class_type == 'combined':
                    btn_color = 'btn-info'
                elif event.class_type == 'returnee':
                    btn_color = 'btn-success'
                elif event.class_type == 'special':
                    btn_color = 'btn-outline-primary'
                cd = timezone.localtime(event.class_date)
                url = reverse('programs:class_registration', kwargs={'beginner_class': event.id})
                data += f'<li><a href="{url}" role="button" type="button" bc_id="{event.id}" class="btn {btn_color} '
                if self.staff or event.state in ['open', 'wait']:
                    data += f'bc-btn m-1" >'
                else:
                    data += f'bc-btn m-1 disabled" >'
                data += f'{event.class_type.capitalize()} {cd.strftime("%I:%M %p")} '
                if event.state == 'wait':
                    data += 'Wait List</a></li>'
                else:
                    data += f'{event.state.capitalize()}</a></li>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {data} </ul></td>"
        return '<td></td>'

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
        cal += '</table>'
        return cal
