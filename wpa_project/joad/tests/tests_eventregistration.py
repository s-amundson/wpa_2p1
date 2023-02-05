import logging
import random
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..models import JoadEvent
from event.models import Event, Registration
from student_app.models.student import Student
logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadEventRegistration(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def set_event(self, event_id):
        event = Event.objects.get(pk=event_id)
        d = timezone.now() + timezone.timedelta(days=7)
        event.event_date = event.event_date.replace(year=d.year, month=d.month, day=d.day)
        event.save()
        return event

    def set_joad_age(self, student, age=None):
        if age is None:
            age = random.randint(10, 19)
        dob = student.dob
        birth = timezone.now().date()
        student.dob = birth.replace(year=birth.year - age, month=dob.month, day=dob.day)
        student.save()

    def test_user_normal_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:event_registration'), secure=True)
        self.assertTemplateUsed(response, 'joad/event_registration.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['form'].fields), 1)

    def test_board_user_get(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:event_registration'), secure=True)
        self.assertTemplateUsed(response, 'joad/event_registration.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['form'].fields), 5)

    def test_student_get(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:event_registration'), secure=True)
        self.assertTemplateUsed(response, 'joad/event_registration.html')
        self.assertEqual(response.status_code, 200)

    def test_student_post(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        self.set_joad_age(Student.objects.get(pk=5))
        event = self.set_event(8)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 8}),
                                    {'event': 8, 'student_5': 'on'}, secure=True)
        # self.assertEqual(response.status_code, 200)
        reg = Registration.objects.all()
        self.assertEqual(len(reg), 2)
        self.assertEqual(self.client.session['line_items'][0]['name'],
                         f'Joad event on {str(event.event_date)[:10]} student: Gary')
        self.assertEqual(self.client.session['payment_category'], 'joad')
        self.assertEqual(self.client.session['payment_description'], f'Joad event on {str(event.event_date)[:10]}')

    def test_student_post_old(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        self.set_event(8)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 8}),
                                    {'event': 8, 'student_5': 'on'}, secure=True)
        # self.assertEqual(response.status_code, 200)
        events = Registration.objects.all()
        self.assertEqual(len(events), 1)
        self.assertContains(response, 'Student is to old.')

    def test_student_post_young(self):
        self.set_joad_age(Student.objects.get(pk=5), 5)
        event = self.set_event(8)
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 8}),
                                    {'event': 8, 'student_5': 'on'}, secure=True)
        events = Registration.objects.all()
        self.assertEqual(len(events), 1)
        self.assertContains(response, 'Student is to young.')

    def test_student_post_reregister(self):
        self.set_joad_age(Student.objects.get(pk=5), 10)
        self.set_event(8)

        Registration.objects.create(event=Event.objects.get(pk=8),
                                    student=Student.objects.get(pk=5),
                                    pay_status='paid',
                                    idempotency_key='7b16fadf-4851-4206-8dc6-81a92b70e52f')
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 8}),
                                    {'event': 8, 'student_5': 'on'}, secure=True)
        # self.assertEqual(response.status_code, 200)
        events = Registration.objects.all()
        self.assertEqual(len(events), 2)
        self.assertRedirects(response, reverse('joad:index'))

    def test_student_post_invalid(self):
        self.set_joad_age(Student.objects.get(pk=5), 10)
        self.set_event(8)

        Registration.objects.create(event=Event.objects.get(pk=8),
                                    student=Student.objects.get(pk=5),
                                    pay_status='paid',
                                    idempotency_key='7b16fadf-4851-4206-8dc6-81a92b70e52f')
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 8}),
                                    {'event': 8}, secure=True)

        events = Registration.objects.all()
        self.assertEqual(len(events), 2)
        self.assertContains(response, 'Invalid student selected')

    def test_student_post_full(self):
        self.set_joad_age(Student.objects.get(pk=5), 10)
        self.set_event(8)
        j = JoadEvent.objects.get(pk=1)
        j.student_limit = 1
        j.save()


        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 8}),
                                    {'event': 8, 'student_5': 'on'}, secure=True)
        events = Registration.objects.all()
        self.assertEqual(len(events), 1)
        self.assertContains(response, 'Class is full')

    def test_student_post_closed(self):
        self.set_joad_age(Student.objects.get(pk=5), 10)
        self.set_event(8)
        j = JoadEvent.objects.get(pk=1)
        j.event.state = 'closed'
        j.event.save()

        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 8}),
                                    {'event': 8, 'student_5': 'on'}, secure=True)
        events = Registration.objects.all()
        self.assertEqual(len(events), 1)

    def test_resume_registration(self):
        self.set_joad_age(Student.objects.get(pk=5), 10)
        self.set_event(8)

        event = Registration.objects.create(event=Event.objects.get(pk=8),
                                         student=Student.objects.get(pk=5),
                                         pay_status='paid',
                                         idempotency_key='7b16fadf-4851-4206-8dc6-81a92b70e52f')
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:resume_event_registration', kwargs={"reg_id": event.id}), secure=True)
        # self.assertEqual(response.status_code, 200)
        events = Registration.objects.all()
        self.assertEqual(len(events), 2)
        self.assertRedirects(response, reverse('payment:make_payment'))
