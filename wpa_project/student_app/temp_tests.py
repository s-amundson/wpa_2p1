# from .tests.tests_beginner_class import TestsBeginnerClass
# from .tests.tests_beginner_class import TestsBeginnerClass2
# from .tests.tests_class_attendance import TestsClassAttendance
# from .tests.tests_class_registration import TestsClassRegistration
# from .tests.tests_class_sign_in import TestsClassSignIn
# from .tests.tests_costs import TestsCosts
# from .tests.tests_email import TestsEmail
# from .tests.tests_index import TestsIndex
# from .tests.tests_payment import TestsPayment
# from .tests.tests_process_payment import TestsProcessPayment
# from .tests.tests_search import TestsClassSearch
# from .tests.tests_square_helper import TestsSquareHelper
# from .tests.tests_student import TestsStudent
# from .tests.tests_student import TestsStudentAPI
# from .tests.tests_student_family import TestsStudentFamily
# from .tests.tests_student_family import TestsStudentFamilyAPI
# from .tests.tests_student_list import TestsSearchList
# from .tests.tests_student_registration import TestsRegisterStudent
# from .tests.tests_theme import TestsTheme
# from .tests.tests_unregister import TestsUnregisterStudent
# from .tests.tests_unregister import TestsUnregisterStudent2

import json
import logging
import time
import uuid
from django.db.models import Q
from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse

from .src import EmailMessage
from .models import BeginnerClass, ClassRegistration, Student, StudentFamily, PaymentLog, User
#
logger = logging.getLogger(__name__)


class TestsTemp(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # self.email_dict = {'total': 5, 'receipt': 'https://example.com',
        #                    'line_items': [{'name': 'Class on None student id: 1',
        #                                    'quantity': '1', 'base_price_money': {'amount': 500, 'currency': 'USD'}}]}

    # def test_class_get(self):
    #     response = self.client.get(reverse('registration:class_registration'), secure=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'student_app/class_registration.html')
    #
    # def test_class_register_good(self):
    #     # add a user to the class<option value="2022-06-05 09:00:00+00:00">05 Jun, 2022 09 AM / 11 AM</option>
    #     self.client.post(reverse('registration:class_registration'),
    #                      {'beginner_class': '1', 'student_1': 'on', 'terms': 'on'}, secure=True)
    #     bc = BeginnerClass.objects.get(pk=1)
    #     self.assertEqual(bc.state, 'open')
    #     cr = ClassRegistration.objects.all()
    #     self.assertEqual(len(cr), 1)
    #     self.assertEqual(cr[0].beginner_class, bc)
    #     self.assertEqual(self.client.session['line_items'][0]['name'],
    #                      'Class on 2022-06-05 student id: 1')
    #     self.assertEqual(self.client.session['payment_db'], 'ClassRegistration')

