import logging
from django.apps import apps
from django.test import TestCase, Client, tag
from django.urls import reverse

from student_app.models import Student
from .helper import create_joad_event
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
                            'inner_scoring': False, 'score': 48, 'attended': True, 'previous_stars': 0,
                            'award_received': False, 'pay_method': 'card'}

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
        self.assertContains(response, 'disabled', 2)

    # @tag('temp')
    def test_get_auth_with_initial(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        pa = PinAttendance.objects.create(bow='barebow',
                                          category='joad_indoor',
                                          distance=9,
                                          inner_scoring=False,
                                          target=60,
                                          score=53,
                                          stars=1,
                                          event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True)
        event = create_joad_event('2022-01-16T16:00:00.000Z', "open")
        pa2 = PinAttendance.objects.create(event=event,
                                          student=Student.objects.get(pk=10),
                                          attended=True)
        response = self.client.get(reverse('joad:event_attendance', kwargs={'event_id': event.id, 'student_id': 10}),
                                   secure=True)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.initial['bow'], pa.bow)
        self.assertEqual(form.initial['distance'], pa.distance)
        self.assertEqual(form.initial['target'], pa.target)
        self.assertTemplateUsed(response, 'joad/pin_attendance.html')
        self.assertContains(response, 'disabled', 2)

    # @tag('temp')
    def test_post_student_bad(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    {'attended': True}, secure=True)
        self.assertEqual(response.status_code, 403)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 0)

    # @tag('temp')
    def test_post_staff_good(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    {'attended': True}, secure=True)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 1)
        self.assertRedirects(response, reverse('joad:event', kwargs={'event_id': 1}), 302)

    # @tag('temp')
    def test_post_student_with_dict_no_record(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    self.attend_dict, secure=True)
        self.assertEqual(response.status_code, 403)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 0)

    # @tag('temp')
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

    # @tag('temp')
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
        self.assertRedirects(response, reverse('payment:make_payment'), 302)
        self.assertIn('Joad Pin(s) for ', self.client.session['line_items'][0]['name'])
        self.assertEqual(self.client.session['payment_category'], 'joad')
        self.assertEqual(self.client.session['payment_description'], 'Joad Pin(s)')
        self.assertEqual(self.client.session['line_items'][0]['quantity'], 1)
        self.assertEqual(self.client.session['line_items'][0]['amount_each'], 5)

    # @tag('temp')
    def test_post_student_with_dict_attend_cash(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True)
        self.attend_dict['pay_method'] = 'cash'
        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    self.attend_dict, secure=True)
        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 1)
        self.assertTrue(pa[0].attended)
        self.assertEqual(pa[0].stars, 1)
        self.assertEqual(pa[0].pay_status, 'cash')
        self.assertRedirects(response, reverse('joad:index'), 302)

    # @tag('temp')
    def test_post_student_with_dict_attend_gold(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        self.attend_dict = {'bow': 'barebow', 'category': 'joad_indoor', 'distance': 18, 'target': 40,
                            'inner_scoring': False, 'score': 273, 'attended': True, 'previous_stars': 9,
                            'award_received': False, 'pay_method': 'card'}
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
        self.assertRedirects(response, reverse('payment:make_payment'), 302)
        self.assertIn('Joad Pin(s) for ', self.client.session['line_items'][0]['name'])
        # self.assertEqual(self.client.session['payment_db'][1], 'PinAttendance')
        self.assertEqual(self.client.session['line_items'][0]['quantity'], 2)
        self.assertEqual(self.client.session['line_items'][0]['amount_each'], 5)

    # @tag('temp')
    def test_post_student_with_dict_attend_no_pin(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        self.attend_dict = {'bow': 'barebow', 'category': 'joad_indoor', 'distance': 18, 'target': 40,
                            'inner_scoring': False, 'score': 253, 'attended': True, 'previous_stars': 9,
                            'award_received': False, 'pay_method': 'card'
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

    # @tag('temp')
    def test_staff_get_award(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True,
                                          previous_stars=2,
                                          pay_status='paid',
                                          idempotency_key='992c77a8-87cc-45af-b390-13d80554e3e0',
                                          award_received=False)
        response = self.client.get(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                   secure=True)
        self.assertContains(response, 'disabled', 4)

    # @tag('temp')
    def test_staff_post_award(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True,
                                          previous_stars=2,
                                          pay_status='paid',
                                          idempotency_key='992c77a8-87cc-45af-b390-13d80554e3e0',
                                          award_received=False)
        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    {'award_received': True}, secure=True)
        self.assertEqual(response.status_code, 302)
        pa2 = PinAttendance.objects.get(pk=pa.id)
        self.assertTrue(pa2.award_received)

    # @tag('temp')
    def test_staff_post_cash_paid(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True,
                                          previous_stars=2,
                                          pay_status='cash',
                                          # idempotency_key='992c77a8-87cc-45af-b390-13d80554e3e0',
                                          award_received=False)
        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    {'pay_method': 'cash', 'payment_received': True}, secure=True)
        self.assertEqual(response.status_code, 302)
        pa2 = PinAttendance.objects.get(pk=pa.id)
        self.assertEqual(pa2.pay_status, 'paid')

    # @tag('temp')
    def test_staff_post_award_cash(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True,
                                          previous_stars=2,
                                          pay_status='cash',
                                          # idempotency_key='992c77a8-87cc-45af-b390-13d80554e3e0',
                                          award_received=False)
        response = self.client.post(reverse('joad:event_attendance', kwargs={'event_id': 1, 'student_id': 10}),
                                    {'payment_received': True, 'award_received': True}, secure=True)
        self.assertEqual(response.status_code, 302)
        pa2 = PinAttendance.objects.get(pk=pa.id)
        self.assertTrue(pa2.award_received)

    # @tag('temp')
    def test_get_attend_list_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:event_attend_list', kwargs={'event_id': 1}),
                                   secure=True)
        self.assertEqual(response.status_code, 403)

    # @tag('temp')
    def test_get_attend_list_auth(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:event_attend_list', kwargs={'event_id': 1}),
                                   secure=True)
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(response.status_code, 200)