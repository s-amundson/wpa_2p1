from django.utils import timezone
from django.urls import reverse
from calendar import HTMLCalendar
from event.models import Event
from joad.models import JoadClass
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
        self.events = Event.objects.filter(event_date__gte=timezone.now().date(),
                                           event_date__year=year,
                                           event_date__month=month).order_by('event_date')
        logger.warning(self.events)
        self.dark = dark
        self.staff = staff
        super(Calendar, self).__init__()
        self.setfirstweekday(6)

    # formats a day as a td
    # filter events by day
    def formatday(self, day):

        data = ''
        if day == 0:
            return '<td></td>'

        for event in self.events.filter(event_date__day=day):
            cd = timezone.localtime(event.event_date)
            data += '</br>'
            if event.type == 'joad class':
                # logging.warning(event.id)
                # logging.warning(event.joadclass_set)
                # logging.warning(JoadClass.objects.filter(event=event))
                jc = JoadClass.objects.filter(event=event).last() # should be able to do this with a reverse relation but not working
                if jc is not None:
                    if event.state in ['open', 'wait', 'full', 'closed', 'canceled']:
                        url = reverse('joad:registration', kwargs={'session_id': jc.session.id})
                        data += f'<a href="{url}" role="button" class="btn btn-warning m-1'
                        if event.state in ['full', 'closed', 'canceled']:
                            data += f' disabled" disabled aria-disabled="true'
                        data += f'"> JOAD Class {cd.strftime("%I:%M %p")} {event.state.capitalize()}</a>'
                else:
                    logging.error('event record mismatch.')

            elif event.type == 'joad event':
                if event.state in ['open', 'wait', 'full', 'closed', 'canceled']:
                    url = reverse('joad:event_registration', kwargs={'event_id': event.id})
                    data += f'<a href="{url}" role="button" class="btn btn-warning m-1'
                    if event.state not in ['open', 'wait']:
                        data += f' disabled" disabled aria-disabled="true'
                    data += f'"> JOAD Pin Shoot {cd.strftime("%I:%M %p")} {event.state.capitalize()}</a>'

            elif event.type == 'class':
                btn_color = 'btn-primary'
                bc = event.beginnerclass_set.last()
                if bc is not None:
                    if bc.class_type == 'combined':
                        btn_color = 'btn-info'
                    elif bc.class_type == 'returnee':
                        btn_color = 'btn-success'
                    elif bc.class_type == 'special':
                        btn_color = 'btn-outline-primary'
                    url = reverse('programs:class_registration', kwargs={'event': event.id})
                    data += f'<a href="{url}" role="button" type="button" bc_id="{event.id}" class="btn {btn_color} '
                    if self.staff or event.state in ['open', 'wait']:
                        data += f'bc-btn m-1" >'
                    else:
                        data += f'bc-btn m-1 disabled" >'
                    data += f'{bc.class_type.capitalize()} {cd.strftime("%I:%M %p")} '
                    if event.state == 'wait':
                        data += 'Wait List</a>'
                    else:
                        data += f'{event.state.capitalize()}</a>'
                else:
                    logging.error(f'event record mismatch. event: {event.id}')
            elif event.type == 'work':
                if event.state in ['open', 'wait', 'full', 'closed', 'canceled']:
                    url = reverse('events:registration', kwargs={'event': event.id})
                    data += f'<a href="{url}" role="button" class="btn btn-work m-1'
                    if event.state not in ['open', 'wait']:
                        data += f' disabled" disabled aria-disabled="true'
                    data += f'"> Work Event {cd.strftime("%I:%M %p")} {event.state.capitalize()}</a>'

        return f"<td><span class='date'>{day}</span>{data}</td>"

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
            bg = 'table-light'
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar table table-bordered">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week)}\n'
        cal += '</table>'
        return cal
