import logging
from unittest.mock import patch

from django.apps import apps
from django.test import TestCase, Client, tag
from django.urls import reverse

from payment.tests import MockSideEffects
from ..models import BeginnerClass
from event.models import Registration
Student = apps.get_model('student_app', 'Student')
User = apps.get_model('student_app', 'User')
logger = logging.getLogger(__name__)


class TestsWait(MockSideEffects, TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def beginner_class_setup(self, id):
        bc = BeginnerClass.objects.get(pk=id)
        bc.beginner_wait_list = 10
        bc.beginner_limit = 0
        bc.returnee_limit = 0
        bc.returnee_wait_limit = 0
        bc.class_type = 'beginner'
        bc.save()
        return bc

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        # update beginner_class
        self.beginner_class = self.beginner_class_setup(1)
        students = [Student.objects.get(pk=2), Student.objects.get(pk=3)]
        self.add_card(self.test_user)
        for s in students:
            cr = Registration(
                event=self.beginner_class.event,
                student=s,
                pay_status="waiting",
                idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
                reg_time='2021-06-09',
                user=self.test_user,
                attended=False)
            cr.save()
        students = [Student.objects.get(pk=4), Student.objects.get(pk=5)]
        for s in students:
            cr = Registration(
                event=self.beginner_class.event,
                student=s,
                # safety_class="2021-05-31",
                pay_status="waiting",
                idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e522",
                reg_time='2021-06-09',
                user=self.test_user,
                attended=False)
            cr.save()

    # @tag('temp')
    def test_get_wait_list(self):
        # Get the page
        response = self.client.get(reverse('programs:admit_wait', kwargs={'event': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/admit_wait.html')
        self.assertEqual(len(response.context['formset']), 4)

        # get same thing with student_family
        response = self.client.get(reverse('programs:admit_wait', kwargs={'event': 1, 'family_id': 2}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/admit_wait.html')
        self.assertEqual(len(response.context['formset']), 2)

    # @tag('temp')
    @patch('program_app.src.class_registration_helper.PaymentHelper.create_payment')
    @patch('program_app.views.admit_wait_view.charge_group.delay')
    def test_post_wait_list(self, chg_group, mock_payment):
        mock_payment.side_effect = self.payment_side_effect
        d = {
            'event': 1,
            'form-TOTAL_FORMS': 4,
            'form-INITIAL_FORMS': 4,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-id': 1,
            'form-0-admit': True,
            'form-1-id': 2,
            'form-1-admit': True,
            'form-2-id': 3,
            'form-2-admit': False,
            'form-3-id': 4,
            'form-3-admit': False,
        }
        response = self.client.post(reverse('programs:admit_wait', kwargs={'event': 1}), d, secure=True)
        self.assertRedirects(response, reverse('programs:admit_wait', kwargs={'event': 1}))
        chg_group.assert_called_with([1, 2])

    # @tag('temp')
    def test_wait_list_returning(self):
        self.beginner_class.class_type = 'returnee'
        self.beginner_class.save()
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('programs:wait_list', kwargs={'event': self.beginner_class.event.id}))
        self.assertTemplateUsed(response, 'program_app/wait_list.html')
        self.assertEqual(len(response.context['object_list']), 2)

    # @tag('temp')
    def test_wait_list_combo(self):
        self.beginner_class.class_type = 'combo'
        self.beginner_class.save()
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('programs:wait_list', kwargs={'event': self.beginner_class.event.id}))
        self.assertTemplateUsed(response, 'program_app/wait_list.html')
        self.assertEqual(len(response.context['object_list']), 2)