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
        self.event = Event.objects.get(pk=8)
        self.post_dict = {
            'event': self.event.id,
            'registration_set-TOTAL_FORMS': 1,
            'registration_set-INITIAL_FORMS': 0,
            'registration_set-MIN_NUM_FORMS': 0,
            'registration_set-MAX_NUM_FORMS': 1000,
            'registration_set-0-register': True,
            'registration_set-0-student': 5,
            'registration_set-0-event': self.event.id,
            }

    def set_event(self, event_id):
        self.event = Event.objects.get(pk=event_id)
        d = timezone.now() + timezone.timedelta(days=7)
        self.event.event_date = self.event.event_date.replace(year=d.year, month=d.month, day=d.day)
        self.event.save()
        return self.event

    def set_joad_age(self, student, age=None):
        if age is None:
            age = random.randint(10, 19)
        dob = student.dob
        birth = timezone.now().date()
        student.dob = birth.replace(year=birth.year - age, month=dob.month, day=dob.day)
        student.is_joad = True
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
        logger.warning(Student.objects.filter(is_joad=True).count())
        # allow user to access
        response = self.client.get(reverse('joad:event_registration'), secure=True)
        self.assertTemplateUsed(response, 'joad/event_registration.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
            '<input type="hidden" name="registration_set-TOTAL_FORMS" value="4" id="id_registration_set-TOTAL_FORMS">')

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
        logger.warning(Registration.objects.all().count())
        response = self.client.post(reverse('joad:event_registration', kwargs={"event": 8}),
                                    self.post_dict, secure=True)
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
        self.set_joad_age(Student.objects.get(pk=5), 25)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event": 8}),
                                    self.post_dict, secure=True)
        # self.assertEqual(response.status_code, 200)
        events = Registration.objects.all()
        self.assertEqual(len(events), 1)
        self.assertContains(response, 'Student must be less then 21 years old to participate')

    def test_student_post_young(self):
        self.set_joad_age(Student.objects.get(pk=5), 5)
        event = self.set_event(8)
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event": 8}),
                                    self.post_dict, secure=True)
        events = Registration.objects.all()
        self.assertEqual(len(events), 1)
        self.assertContains(response, 'Student must be at least 8 years old to participate')

    def test_student_post_reregister(self):
        self.set_joad_age(Student.objects.get(pk=5), 10)
        self.set_event(8)

        Registration.objects.create(event=Event.objects.get(pk=8),
                                    student=Student.objects.get(pk=5),
                                    pay_status='paid',
                                    idempotency_key='7b16fadf-4851-4206-8dc6-81a92b70e52f')
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event": 8}),
                                    self.post_dict, secure=True)
        # self.assertEqual(response.status_code, 200)
        events = Registration.objects.all()
        self.assertEqual(len(events), 2)
        self.assertContains(response, 'Student is already enrolled')

    def test_student_post_invalid(self):
        self.set_joad_age(Student.objects.get(pk=5), 10)
        self.set_event(8)

        Registration.objects.create(event=Event.objects.get(pk=8),
                                    student=Student.objects.get(pk=5),
                                    pay_status='paid',
                                    idempotency_key='7b16fadf-4851-4206-8dc6-81a92b70e52f')
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event": 8}),
                                    {'event': 8}, secure=True)
        # response = self.client.post(reverse('joad:event_registration', kwargs={"event": 8}),
        #                             self.post_dict, secure=True)
        events = Registration.objects.all()
        self.assertEqual(len(events), 2)
        self.assertContains(response, 'Error with form')

    def test_student_post_full(self):
        self.set_joad_age(Student.objects.get(pk=5), 10)
        self.set_event(8)
        j = JoadEvent.objects.get(pk=1)
        j.student_limit = 1
        j.save()


        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event": 8}),
                                    self.post_dict, secure=True)
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

        response = self.client.post(reverse('joad:event_registration', kwargs={"event": 8}),
                                    self.post_dict, secure=True)
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
