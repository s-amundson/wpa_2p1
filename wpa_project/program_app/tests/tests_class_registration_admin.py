import logging

from django.test import TestCase, Client, tag
from django.urls import reverse
from django.utils import timezone

from ..models import BeginnerClass
from event.models import Event, Registration
from student_app.models import Student, User

logger = logging.getLogger(__name__)


class TestsClassAdminRegistration(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.event = Event.objects.get(pk=1)
        self.event.event_date = timezone.now() + timezone.timedelta(days=5)
        self.event.save()
        self.post_dict = {
            'event': [self.event.id],
            'terms': True,
            'student': 4,
            'student_family': 3,
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-register': True,
            'form-0-student': 4,
            'form-1-register': True,
            'form-1-student': 5,
            }
        return self.post_dict

    def test_class_get_no_auth(self):
        # Check that staff cannot access
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('programs:class_registration_admin', kwargs={'family_id': 4}), secure=True)
        self.assertEqual(response.status_code, 403)
        # self.assertTemplateUsed(response, 'program_app/class_registration.html')

    def test_class_get_no_auth2(self):
        # Check that cannot access logged out
        self.client.logout()
        response = self.client.get(reverse('programs:class_registration_admin', kwargs={'family_id': 4}), secure=True)
        self.assertEqual(response.status_code, 302)

    def test_class_get_auth(self):
        # Check that board can access
        response = self.client.get(reverse('programs:class_registration_admin', kwargs={'family_id': 4}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'program_app/class_registration.html')

    def test_class_post_good(self):
        self.post_dict['student'] = 4
        response = self.client.post(reverse('programs:class_registration_admin', kwargs={'family_id': 3}),
                                    self.post_dict, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 2)
        for c in cr:
            self.assertEqual(c.pay_status, 'admin')
        self.assertRedirects(response, reverse('events:event_attend_list', kwargs={'event': 1}))

    def test_add_student_to_full(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.beginner_limit = 1
        bc.event.state = 'full'
        bc.event.save()
        bc.save()

        s = Student.objects.get(pk=5)
        s.safety_class = None
        s.save()
        response = self.client.post(reverse('programs:class_registration_admin', kwargs={'family_id': 3}),
                                    self.post_dict, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'full')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 2)
        for c in cr:
            self.assertEqual(c.pay_status, 'admin')
        self.assertRedirects(response, reverse('events:event_attend_list', kwargs={'event': 1}))

    def test_add_student_to_closed(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.beginner_limit = 1
        bc.event.state = 'closed'
        bc.event.save()
        bc.save()

        s = Student.objects.get(pk=5)
        s.safety_class = None
        s.save()

        response = self.client.post(reverse('programs:class_registration_admin', kwargs={'family_id': 3}),
                                    self.post_dict, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'closed')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 2)
        for c in cr:
            self.assertEqual(c.pay_status, 'admin')
        self.assertRedirects(response, reverse('events:event_attend_list', kwargs={'event': 1}))

    def test_add_student_registered(self):
        bc = BeginnerClass.objects.get(pk=1)
        s = Student.objects.get(pk=4)
        cr = Registration(
            event=bc.event,
            student=s,
            pay_status="paid",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)
        cr.save()
        response = self.client.post(reverse('programs:class_registration_admin', kwargs={'family_id': 3}),
                                    self.post_dict, secure=True)
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertContains(response, 'Student is already enrolled')

    # @tag('temp')
    def test_add_student_registered_admin(self):
        bc = BeginnerClass.objects.get(pk=1)
        s = Student.objects.get(pk=4)
        cr = Registration(
            event=bc.event,
            student=s,
            pay_status="admin",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)
        cr.save()
        response = self.client.post(reverse('programs:class_registration_admin', kwargs={'family_id': 3}),
                                    self.post_dict, secure=True)
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertContains(response, 'Student is already enrolled')

    def test_class_add_student_after_class(self):
        bc = BeginnerClass.objects.get(pk=1)
        # bc.class_date = timezone.now() - timezone.timedelta(hours=3)
        bc.event.state = 'closed'
        bc.event.save()
        bc.save()

        response = self.client.post(reverse('programs:class_registration_admin', kwargs={'family_id': 3}),
                                    self.post_dict, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'closed')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 2)
        for c in cr:
            self.assertEqual(c.pay_status, 'admin')
        self.assertRedirects(response, reverse('events:event_attend_list', kwargs={'event': 1}))

    def test_class_post_good_pay(self):
        self.post_dict['payment'] = 'on'
        response = self.client.post(reverse('programs:class_registration_admin', kwargs={'family_id': 3}),
                                    self.post_dict, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 2)
        for c in cr:
            self.assertEqual(c.pay_status, 'start')
        self.assertEqual(len(self.client.session['line_items']), 2)
        self.assertRedirects(response, reverse('payment:make_payment'))
