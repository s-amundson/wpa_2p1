import logging
import uuid
import json

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..models import BeginnerClass
from event.models import Registration
Student = apps.get_model('student_app', 'Student')
User = apps.get_model('student_app', 'User')
logger = logging.getLogger(__name__)


class TestsClassAttendance(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_class_attendance(self):
        # Get the page
        response = self.client.get(reverse('programs:class_attend_list', kwargs={'event': 1}), secure=True)
        # list the class students but since class is not closed Attending column is missing
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_attendance.html')
        self.assertContains(response, 'Attending', 3)

        # change user, then add 2 new.
        self.client.force_login(User.objects.get(pk=2))
        self.client.post(reverse('programs:class_registration'), {'beginner_class': 1, 'student_2': 'on',
                                                                  'student_3': 'on', 'terms': 'on'}, secure=True)
        # change user, then add 1 returnee.
        self.client.force_login(User.objects.get(pk=4))
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': 1, 'student_6': 'on', 'terms': 'on'}, secure=True)

        self.client.force_login(User.objects.get(pk=1))
        self.client.get(reverse('programs:class_attend_list', kwargs={'event': 1}), secure=True)

        # set pay status to paid
        cr = Registration.objects.all()
        for c in cr:
            c.pay_status = 'paid'
            c.save()

        # close the class
        response = self.client.post(reverse('programs:beginner_class', kwargs={'beginner_class': 1}),
                                    {'class_date': "2023-06-05 09:00:00", 'class_type': 'combined', 'beginner_limit': 2,
                                     'beginner_wait_limit': 0, 'returnee_limit': 2, 'returnee_wait_limit': 0,
                                     'instructor_limit': 2, 'state': 'closed', 'cost': 5},
                                    secure=True)
        self.assertEqual(response.status_code, 302)
        # check that the attending column is there with checkboxes
        response = self.client.get(reverse('programs:class_attend_list', kwargs={'event': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Attending', 6)

    def test_class_beginner_attendance(self):
        # register instructor and close class.
        bc = BeginnerClass.objects.get(pk=1)
        cr = Registration(event=bc.event,
                               student=Student.objects.get(pk=1),
                               pay_status='paid',
                               idempotency_key=str(uuid.uuid4()))
        cr.save()
        bc.event.state = 'closed'
        bc.event.save()

        # check that the attending column is there with checkboxes
        response = self.client.get(reverse('programs:class_attend_list', kwargs={'event': 1}), secure=True)
        self.assertEqual(response.status_code, 200)

        # mark instructor as attending.
        self.client.post(reverse('programs:class_attend', kwargs={'registration': cr.id}),
                         {'check_1': 'on'}, secure=True)

        cr = Registration.objects.get(pk=cr.pk)
        self.assertEqual(cr.attended, True)
        self.assertEqual(cr.student.safety_class, timezone.datetime.date(bc.event.event_date))

        # check that the attending column is there with checkboxes
        response = self.client.get(reverse('programs:class_attend_list', kwargs={'event': 1}), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_class_beginner_unattend(self):
        # register instructor and close class.
        bc = BeginnerClass.objects.get(pk=1)
        cr = Registration(event=bc.event,
                          student=Student.objects.get(pk=1),
                          pay_status='paid',
                          idempotency_key=str(uuid.uuid4()))
        cr.save()
        bc.event.state = 'closed'
        bc.event.save()

        # mark instructor as attending.
        self.client.post(reverse('programs:class_attend', kwargs={'registration': cr.id}),
                         {'check_1': ''}, secure=True)

        cr = Registration.objects.get(pk=cr.pk)
        self.assertEqual(cr.attended, False)
        self.assertIsNone(cr.student.safety_class)

    def test_class_instructor_attendance(self):
        # make user instructor
        u = User.objects.get(pk=1)
        u.is_instructor = True
        u.save()

        # register instructor and close class.
        bc = BeginnerClass.objects.get(pk=1)
        cr = Registration(event=bc.event,
                          student=Student.objects.get(pk=1),
                          pay_status='paid',
                          idempotency_key=str(uuid.uuid4()))
        cr.save()
        bc.event.state = 'closed'
        bc.event.save()

        # check that the attending column is there with checkboxes
        response = self.client.get(reverse('programs:class_attend_list', kwargs={'event': 1}), secure=True)
        self.assertEqual(response.status_code, 200)

        # mark instructor as attending.
        self.client.post(reverse('programs:class_attend', kwargs={'registration': cr.id}),
                         {'check_1': 'on'}, secure=True)

        cr = Registration.objects.get(pk=cr.pk)
        self.assertEqual(cr.attended, True)

        # check that the attending column is there with checkboxes
        response = self.client.get(reverse('programs:class_attend_list', kwargs={'event': 1}), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_class_attend_error(self):

        # register student and close class.
        bc = BeginnerClass.objects.get(pk=1)
        cr = Registration(event=bc.event,
                          student=Student.objects.get(pk=3),
                          pay_status='paid',
                          idempotency_key=str(uuid.uuid4()))
        cr.save()
        bc.event.state = 'closed'
        bc.event.save()

        # mark instructor as attending.
        response = self.client.post(reverse('programs:class_attend', kwargs={'registration': cr.id}),
                         {'check_A': 'on'}, secure=True)

        cr = Registration.objects.get(pk=cr.pk)
        self.assertEqual(cr.attended, False)
        content = json.loads(response.content)
        self.assertTrue(content['error'])

    def test_class_unattend(self):

        # register student and close class.
        bc = BeginnerClass.objects.get(pk=1)
        cr = Registration(event=bc.event,
                          student=Student.objects.get(pk=3),
                          pay_status='paid',
                          idempotency_key=str(uuid.uuid4()),
                          attended=True)
        cr.save()
        cr.student.safety_class = bc.event.event_date
        cr.student.save()
        bc.event.state = 'closed'
        bc.event.save()

        # mark instructor as attending.
        response = self.client.post(reverse('programs:class_attend', kwargs={'registration': cr.id}),
                         {'check_3': 'off'}, secure=True)

        cr = Registration.objects.get(pk=cr.pk)
        self.assertEqual(cr.attended, False)
        content = json.loads(response.content)
        self.assertFalse(content['error'])
        self.assertIsNone(cr.student.safety_class)
