import logging

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse

from ..models import ClassRegistration
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

    def test_class_attendance(self):
        # Get the page
        self.client.force_login(self.test_user)

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

        # close the class
        response = self.client.post(reverse('programs:beginner_class', kwargs={'beginner_class': 1}),
                                    {'class_date': "2022-06-05", 'beginner_limit': 2, 'returnee_limit': 2,
                                     'state': 'closed', 'cost': 5}, secure=True)
        self.assertEqual(response.status_code, 302)
        # TODO check payment status
        # check that the attending column is there with checkboxes
        response = self.client.get(reverse('programs:beginner_class', kwargs={'beginner_class': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Attending')
        self.assertContains(response, 'check_2')
        self.assertContains(response, 'check_3')

        # Mark the students as attending and check the records were updated.
        self.client.post(reverse('programs:beginner_class', kwargs={'beginner_class': 1}),
                         {'attendee_form': 'on', 'check_2': 'on', 'check_3': 'on'}, secure=True)
        cr = ClassRegistration.objects.all()
        self.assertEqual(cr[0].attended, True)
        self.assertEqual(cr[1].attended, True)
        self.assertNotEquals(cr[0].student.safety_class, None)
        self.assertNotEquals(cr[1].student.safety_class, None)

        # Mark a student as not attending and check the records.
        self.client.post(reverse('programs:beginner_class', kwargs={'beginner_class': 1}),
                         {'attendee_form': 'on', 'check_3': 'on'}, secure=True)
        cr = ClassRegistration.objects.all()
        self.assertEqual(cr[0].attended, False)
        self.assertEqual(cr[1].attended, True)
        self.assertEquals(cr[0].student.safety_class, None)
        self.assertNotEquals(cr[1].student.safety_class, None)
