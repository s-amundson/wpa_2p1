import logging
from unittest.mock import patch

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse

from payment.tests import MockSideEffects
from ..models import BeginnerClass, ClassRegistration
Student = apps.get_model('student_app', 'Student')
User = apps.get_model('student_app', 'User')
logger = logging.getLogger(__name__)


class TestsAdmitWait(MockSideEffects, TestCase):
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
            cr = ClassRegistration(
                beginner_class=self.beginner_class,
                student=s,
                new_student=True,
                pay_status="waiting",
                idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
                reg_time='2021-06-09',
                user=self.test_user,
                attended=False)
            cr.save()
        students = [Student.objects.get(pk=4), Student.objects.get(pk=5)]
        for s in students:
            cr = ClassRegistration(
                beginner_class=self.beginner_class,
                student=s,
                new_student=True,
                # safety_class="2021-05-31",
                pay_status="waiting",
                idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e522",
                reg_time='2021-06-09',
                user=self.test_user,
                attended=False)
            cr.save()

    def test_get_wait_list(self):
        # Get the page
        response = self.client.get(reverse('programs:admit_wait', kwargs={'beginner_class': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/admit_wait.html')
        self.assertEqual(len(response.context['form'].fields), 4)

        # get same thing with student_family
        response = self.client.get(reverse('programs:admit_wait', kwargs={'beginner_class': 1, 'family_id': 2}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/admit_wait.html')
        self.assertEqual(len(response.context['form'].fields), 2)

    @patch('program_app.src.class_registration_helper.PaymentHelper.create_payment')
    @patch('program_app.forms.admit_wait_form.charge_group.delay')
    def test_post_wait_list(self, chg_group, mock_payment):
        mock_payment.side_effect = self.payment_side_effect
        d = {'admit_1': True, 'admit_2': True, 'admit_3': False, 'admit_4': False}
        response = self.client.post(reverse('programs:admit_wait', kwargs={'beginner_class': 1}), d, secure=True)
        self.assertRedirects(response, reverse('programs:class_attend_list', kwargs={'beginner_class': 1}))
        chg_group.assert_called_with([2, 1])

