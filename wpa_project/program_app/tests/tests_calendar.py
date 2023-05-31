import logging

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..src.calendar import Calendar
from .helper import create_beginner_class
from event.models import Event, VolunteerEvent
from joad.models import JoadClass, JoadEvent, Session
logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsCalendar(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_UID = 3

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_calendar(self):
        date = timezone.datetime.now() + timezone.timedelta(days=1)
        date = date.replace(hour=9, minute=0, second=0, microsecond=0)
        bc1 = create_beginner_class(date, 'wait', 'beginner')
        bc2 = create_beginner_class(date.replace(hour=11), 'wait', 'returnee')
        bc3 = create_beginner_class(date.replace(hour=13), 'open', 'beginner')
        bc4 = create_beginner_class(date.replace(hour=15), 'open', 'returnee')
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('programs:calendar'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['beginner_wait'], bc1)
        self.assertEqual(response.context['returnee_wait'], bc2)
        self.assertEqual(response.context['beginner_class'], bc3)
        self.assertEqual(response.context['returnee_class'], bc4)

    def test_get_calendar_date(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('programs:calendar', kwargs={'year': 2023, 'month': 14}), secure=True)
        self.assertEqual(response.status_code, 200)


    def test_day(self):
        date = timezone.datetime.now() + timezone.timedelta(days=1)
        date = date.replace(hour=9, minute=0, second=0, microsecond=0)
        create_beginner_class(date, 'open', 'beginner')
        create_beginner_class(date.replace(hour=11), 'open', 'returnee')
        create_beginner_class(date.replace(hour=15), 'open', 'combined')
        session = Session.objects.create(cost=120, start_date=date, state='open', student_limit=12)
        jc = JoadClass.objects.create(
            event=Event.objects.create(event_date=date.replace(hour=10), state='open', type='joad class'),
            session=session)
        je = JoadEvent.objects.create(
            event=Event.objects.create(
                event_date=date.replace(hour=13),
                state='open',
                cost_standard=15,
                cost_member=15,
                type='joad event'),
            event_type="joad_indoor",
            student_limit=10,
            pin_cost=5)
        ve = VolunteerEvent.objects.create(
            event=Event.objects.create(
                event_date=date.replace(hour=15),
                state='open',
                cost_standard=0,
                cost_member=0,
                type='work'),
            description='test description'
        )
        cal = Calendar(year=date.year, month=date.month)
        html_cal = cal.formatmonth(withyear=True)
        logging.warning(html_cal)
        self.assertEqual(html_cal.count('Beginner 09:00 AM'), 1)
        self.assertEqual(html_cal.count('Returnee 11:00 AM'), 1)
        self.assertEqual(html_cal.count('Combined 03:00 PM'), 1)
        self.assertEqual(html_cal.count('JOAD Class 10:00 AM'), 1)
        self.assertEqual(html_cal.count('JOAD Pin Shoot 01:00 PM'), 1)
        self.assertEqual(html_cal.count('Work Event 03:00 PM'), 1)

    def test_day_closed(self):
        date = timezone.datetime.now() + timezone.timedelta(days=1)
        date = date.replace(hour=9, minute=0, second=0, microsecond=0)
        create_beginner_class(date, 'closed', 'beginner')
        create_beginner_class(date.replace(hour=11), 'closed', 'returnee')
        create_beginner_class(date.replace(hour=15), 'closed', 'combined')
        session = Session.objects.create(cost=120, start_date=date, state='closed', student_limit=12)
        jc = JoadClass.objects.create(
            event=Event.objects.create(event_date=date.replace(hour=10), state='closed', type='joad class'),
            session=session)
        je = JoadEvent.objects.create(
            event=Event.objects.create(
                event_date=date.replace(hour=13),
                state='closed',
                cost_standard=15,
                cost_member=15,
                type='joad event'),
            event_type="joad_indoor",
            student_limit=10,
            pin_cost=5)
        ve = VolunteerEvent.objects.create(
            event=Event.objects.create(
                event_date=date.replace(hour=15),
                state='closed',
                cost_standard=0,
                cost_member=0,
                type='work'),
            description='test description'
        )
        cal = Calendar(year=date.year, month=date.month)
        html_cal = cal.formatmonth(withyear=True)
        logging.warning(html_cal)
        self.assertEqual(html_cal.count('Beginner 09:00 AM Closed'), 1)
        self.assertEqual(html_cal.count('Returnee 11:00 AM Closed'), 1)
        self.assertEqual(html_cal.count('Combined 03:00 PM Closed'), 1)
        self.assertEqual(html_cal.count('JOAD Class 10:00 AM Closed'), 1)
        self.assertEqual(html_cal.count('JOAD Pin Shoot 01:00 PM Closed'), 1)
        self.assertEqual(html_cal.count('Work Event 03:00 PM Closed'), 1)

    def test_get_event_calendar(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('programs:google_calendar'), secure=True)
        self.assertEqual(response.status_code, 200)