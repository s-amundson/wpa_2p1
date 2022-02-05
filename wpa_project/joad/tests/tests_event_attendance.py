import logging
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse

from student_app.models import Student
from ..models import JoadEvent, PinAttendance

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsEventAttendance(TestCase):
    fixtures = ['f1', 'joad1', 'joad_registration', 'pinscores']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.student_dict = {'session': 1, 'student_8': True}
        self.attend_dict = {'bow': 'barebow', 'category': 'joad_indoor', 'distance': 9, 'target': 60,
            'inner_scoring': False, 'score': 48, 'attended': True, 'previous_stars': 0, 'award_received': False}

    def test_get_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                   secure=True)
        self.assertEqual(response.status_code, 403)

    def test_get_auth(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True)

        response = self.client.get(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                   secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'joad/pin_attendance.html')

    def test_post_student_bad(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    {'attended': True}, secure=True)
        self.assertEqual(response.status_code, 403)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 0)

    def test_post_staff_good(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    {'attended': True}, secure=True)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 1)
        self.assertRedirects(response, reverse('joad:event', kwargs={'event_id': 1}), 302)

    def test_post_student_with_dict_no_record(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    self.attend_dict, secure=True)
        self.assertEqual(response.status_code, 403)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 0)

    def test_post_student_with_dict_not_attend(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=False)

        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    self.attend_dict, secure=True)
        self.assertEqual(response.status_code, 403)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 1)

    def test_post_student_with_dict_attend(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True)

        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    self.attend_dict, secure=True)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 1)
        self.assertTrue(pa[0].attended)
        self.assertEqual(pa[0].stars, 1)
        self.assertRedirects(response, reverse('payment:process_payment'), 302)
        self.assertIn('Joad Pin(s) for ', self.client.session['line_items'][0]['name'])
        self.assertEqual(self.client.session['payment_db'][1], 'PinAttendance')
        self.assertEqual(self.client.session['line_items'][0]['quantity'], '1')
        self.assertEqual(self.client.session['line_items'][0]['base_price_money']['amount'], 500)


    def test_post_student_with_dict_attend_gold(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        self.attend_dict = {'bow': 'barebow', 'category': 'joad_indoor', 'distance': 18, 'target': 40,
            'inner_scoring': False, 'score': 273, 'attended': True, 'previous_stars': 9, 'award_received': False
        }
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True)

        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    self.attend_dict, secure=True)
        # self.assertEqual(response.status_code, 200)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 1)
        self.assertTrue(pa[0].attended)
        self.assertEqual(pa[0].stars, 11)
        self.assertRedirects(response, reverse('payment:process_payment'), 302)
        self.assertIn('Joad Pin(s) for ', self.client.session['line_items'][0]['name'])
        self.assertEqual(self.client.session['payment_db'][1], 'PinAttendance')
        self.assertEqual(self.client.session['line_items'][0]['quantity'], '2')
        self.assertEqual(self.client.session['line_items'][0]['base_price_money']['amount'], 1000)

    def test_post_student_with_dict_attend_no_pin(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        self.attend_dict = {'bow': 'barebow', 'category': 'joad_indoor', 'distance': 18, 'target': 40,
                            'inner_scoring': False, 'score': 253, 'attended': True, 'previous_stars': 9,
                            'award_received': False
                            }
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True)

        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    self.attend_dict, secure=True)
        # self.assertEqual(response.status_code, 200)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 1)
        self.assertTrue(pa[0].attended)
        self.assertEqual(pa[0].stars, 9)
        self.assertRedirects(response, reverse('joad:index'), 302)
        # messages = list(response.context['messages'])
        # self.assertEqual(str(messages[0]), "No pins earned today. Thank you")
