import logging

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..src.calendar import Calendar
from ..models import BeginnerClass
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
        logging.debug('here')

    def test_get_calendar(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('programs:class_calendar'), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_insert_event(self):
        cal = Calendar()
        start_list = [
            cal.Event(id=1, class_date=timezone.datetime(year=2022, month=2, day=2, hour=9), class_type='test_type1',
                      state='test_state'),
            cal.Event(id=1, class_date=timezone.datetime(year=2022, month=2, day=2, hour=11), class_type='test_type3',
                      state='test_state')
        ]
        e2 = cal.Event(id=1, class_date=timezone.datetime(year=2022, month=2, day=2, hour=10), class_type='test_type2',
                       state='test_state')
        end_list = cal.insert_event(start_list, e2)
        logging.debug(end_list[1].class_date)
        self.assertEqual(end_list[1].class_date, e2.class_date)
        self.assertEqual(len(end_list), 3)

    def test_insert_event_last(self):
        cal = Calendar()
        start_list = [
            cal.Event(id=1, class_date=timezone.datetime(year=2022, month=2, day=2, hour=9), class_type='test_type1',
                      state='test_state'),
            cal.Event(id=1, class_date=timezone.datetime(year=2022, month=2, day=2, hour=11), class_type='test_type3',
                      state='test_state')
        ]
        e2 = cal.Event(id=1, class_date=timezone.datetime(year=2022, month=2, day=2, hour=12), class_type='test_type2',
                       state='test_state')
        end_list = cal.insert_event(start_list, e2)
        logging.debug(end_list[1].class_date)
        self.assertEqual(end_list[2].class_date, e2.class_date)
        self.assertEqual(len(end_list), 3)

    def test_day(self):
        date = timezone.datetime.now() + timezone.timedelta(days=1)
        date = date.replace(hour=9, minute=0, second=0, microsecond=0)
        logging.debug(date)
        BeginnerClass.objects.create(class_date=date, class_type='beginner', beginner_limit=2, returnee_limit=2,
                                          state='open')
        BeginnerClass.objects.create(class_date=date.replace(hour=11), class_type='returnee', beginner_limit=2,
                                     returnee_limit=2, state='open')
        BeginnerClass.objects.create(class_date=date.replace(hour=15), class_type='combined', beginner_limit=2,
                                     returnee_limit=2, state='open')
        session = Session.objects.create(cost=120, start_date=date, state='open', student_limit=12)
        jc = JoadClass.objects.create(class_date=date.replace(hour=10), session=session, state='open')
        je = JoadEvent.objects.create(cost=15, event_date=date.replace(hour=13), event_type="joad_indoor", state='open',
                                      student_limit=10, pin_cost=5)

        cal = Calendar(year=date.year, month=date.month)
        html_cal = cal.formatmonth(withyear=True)
        logging.debug(html_cal)
        self.assertEqual(html_cal.count('Beginner 09:00 AM'), 1)
        self.assertEqual(html_cal.count('Returnee 11:00 AM'), 1)
        self.assertEqual(html_cal.count('Combined 03:00 PM'), 1)
        self.assertEqual(html_cal.count('JOAD Class 10:00 AM'), 1)
        self.assertEqual(html_cal.count('JOAD Pin Shoot 01:00 PM'), 1)

    def test_day_closed(self):
        date = timezone.datetime.now() + timezone.timedelta(days=1)
        date = date.replace(hour=9, minute=0, second=0, microsecond=0)
        logging.debug(date)
        BeginnerClass.objects.create(class_date=date, class_type='beginner', beginner_limit=2, returnee_limit=2,
                                          state='closed')
        BeginnerClass.objects.create(class_date=date.replace(hour=11), class_type='returnee', beginner_limit=2,
                                     returnee_limit=2, state='closed')
        BeginnerClass.objects.create(class_date=date.replace(hour=15), class_type='combined', beginner_limit=2,
                                     returnee_limit=2, state='closed')
        session = Session.objects.create(cost=120, start_date=date, state='closed', student_limit=12)
        jc = JoadClass.objects.create(class_date=date.replace(hour=10), session=session, state='past')
        je = JoadEvent.objects.create(cost=15, event_date=date.replace(hour=13), event_type="joad_indoor",
                                      state='closed', student_limit=10, pin_cost=5)

        cal = Calendar(year=date.year, month=date.month)
        html_cal = cal.formatmonth(withyear=True)
        self.assertEqual(html_cal.count('Beginner 09:00 AM FULL'), 1)
        self.assertEqual(html_cal.count('Returnee 11:00 AM FULL'), 1)
        self.assertEqual(html_cal.count('Combined 03:00 PM FULL'), 1)
        self.assertEqual(html_cal.count('JOAD Class 10:00 AM CLOSED'), 1)
        self.assertEqual(html_cal.count('JOAD Pin Shoot 01:00 PM CLOSED'), 1)