import logging
import uuid

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..models import BeginnerClass, ClassRegistration
Student = apps.get_model('student_app', 'Student')
User = apps.get_model('student_app', 'User')
logger = logging.getLogger(__name__)


class TestsClassAttendance(TestCase):
    fixtures = ['f1', 'f3']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_class_attendance(self):
        # Get the page
        response = self.client.get(reverse('programs:beginner_class', kwargs={'beginner_class': 1}), secure=True)
        # list the class students but since class is not closed Attending column is missing
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/beginner_class.html')
        # logging.debug(response.content)
        self.assertContains(response, '<input type="hidden" name="attendee_form" value="on">', html=True)
        self.assertNotContains(response, 'Attending')

        # change user, then add 2 new.
        self.client.force_login(User.objects.get(pk=2))
        self.client.post(reverse('programs:class_registration'), {'beginner_class': 1, 'student_2': 'on',
                                                                  'student_3': 'on', 'terms': 'on'}, secure=True)
        # change user, then add 1 returnee.
        self.client.force_login(User.objects.get(pk=4))
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': 1, 'student_6': 'on', 'terms': 'on'}, secure=True)

        self.client.force_login(User.objects.get(pk=1))
        self.client.get(reverse('programs:beginner_class', kwargs={'beginner_class': 1}), secure=True)

        # set pay status to paid
        cr = ClassRegistration.objects.all()
        for c in cr:
            c.pay_status = 'paid'
            c.save()

        # close the class
        response = self.client.post(reverse('programs:beginner_class', kwargs={'beginner_class': 1}),
                                    {'class_date': "2022-06-05", 'class_type': 'combined', 'beginner_limit': 2,
                                     'returnee_limit': 2, 'instructor_limit': 2, 'state': 'closed', 'cost': 5},
                                    secure=True)
        self.assertEqual(response.status_code, 302)
        # TODO check payment status
        # check that the attending column is there with checkboxes
        response = self.client.get(reverse('programs:beginner_class', kwargs={'beginner_class': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Attending')
        self.assertContains(response, 'covid_vax_2')
        self.assertContains(response, 'covid_vax_3')

    def test_class_beginner_attendance(self):
        # register instructor and close class.
        bc = BeginnerClass.objects.get(pk=1)
        cr = ClassRegistration(beginner_class=bc,
                               student=Student.objects.get(pk=1),
                               new_student=False,
                               pay_status='paid',
                               idempotency_key=str(uuid.uuid4()))
        cr.save()
        bc.state = 'closed'
        bc.save()

        # check that the attending column is there with checkboxes
        response = self.client.get(reverse('programs:beginner_class', kwargs={'beginner_class': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'check_1')

        # mark instructor as attending.
        self.client.post(reverse('programs:class_attend', kwargs={'registration': cr.id}),
                         {'check_1': 'on'}, secure=True)

        cr = ClassRegistration.objects.get(pk=cr.pk)
        self.assertEqual(cr.attended, True)
        self.assertEqual(cr.student.safety_class, timezone.datetime.date(bc.class_date))

    def test_class_beginner_unattend(self):
        # register instructor and close class.
        bc = BeginnerClass.objects.get(pk=1)
        cr = ClassRegistration(beginner_class=bc,
                               student=Student.objects.get(pk=1),
                               new_student=False,
                               pay_status='paid',
                               idempotency_key=str(uuid.uuid4()))
        cr.save()
        bc.state = 'closed'
        bc.save()

        # mark instructor as attending.
        self.client.post(reverse('programs:class_attend', kwargs={'registration': cr.id}),
                         {'check_1': ''}, secure=True)

        cr = ClassRegistration.objects.get(pk=cr.pk)
        self.assertEqual(cr.attended, False)
        self.assertIsNone(cr.student.safety_class)

    def test_class_instructor_attendance(self):
        # make user instructor
        u = User.objects.get(pk=1)
        u.is_instructor = True
        u.save()

        # register instructor and close class.
        bc = BeginnerClass.objects.get(pk=1)
        cr = ClassRegistration(beginner_class=bc,
                               student=Student.objects.get(pk=1),
                               new_student=False,
                               pay_status='paid',
                               idempotency_key=str(uuid.uuid4()))
        cr.save()
        bc.state = 'closed'
        bc.save()

        # check that the attending column is there with checkboxes
        response = self.client.get(reverse('programs:beginner_class', kwargs={'beginner_class': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'check_1')

        # mark instructor as attending.
        self.client.post(reverse('programs:class_attend', kwargs={'registration': cr.id}),
                         {'check_1': 'on'}, secure=True)

        cr = ClassRegistration.objects.get(pk=cr.pk)
        self.assertEqual(cr.attended, True)
