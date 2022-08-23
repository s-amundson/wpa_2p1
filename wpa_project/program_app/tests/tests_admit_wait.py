import logging
import uuid
import json
from unittest.mock import patch

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from payment.models import Card, Customer
from ..models import BeginnerClass, ClassRegistration
from ..tasks import charge_group
Student = apps.get_model('student_app', 'Student')
User = apps.get_model('student_app', 'User')
logger = logging.getLogger(__name__)


class TestsAdmitWait(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_card(self, user):
        customer = Customer.objects.create(user=user,
                                           customer_id="9Z9Q0D09F0WMV0FHFA2QMZH8SC",
                                           created_at="2022-05-30T19:50:46Z",
                                           creation_source="THIRD_PARTY",
                                           updated_at="2022-05-30T19:50:46Z")
        card = Card.objects.create(
            bin=411111,
            card_brand="VISA",
            card_id="ccof:8sLQqf1boPfmwDKI4GB",
            card_type="CREDIT",
            cardholder_name="",
            customer=customer,
            default=1,
            enabled=1,
            exp_month=11,
            exp_year=2022,
            fingerprint="sq-1-npXvWJT5AhTtISQwBYohbA8kkQ24CyPCN6G6kP_6Bm_K2KPYsT1y_1xKUhvAnMIzfA",
            id=1,
            last_4=1111,
            merchant_id="TYXMY2T8CN2PK",
            prepaid_type="NOT_PREPAID",
            version=0)
        return card

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
        settings.SQUARE_TESTING = True
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

    @patch('program_app.forms.admit_wait_form.charge_group.delay')
    def test_post_wait_list(self, chg_group):
        d = {'admit_1': True, 'admit_2': True, 'admit_3': False, 'admit_4': False}
        response = self.client.post(reverse('programs:admit_wait', kwargs={'beginner_class': 1}), d, secure=True)
        self.assertRedirects(response, reverse('programs:class_attend_list', kwargs={'beginner_class': 1}))
        chg_group.assert_called_with([2, 1])

