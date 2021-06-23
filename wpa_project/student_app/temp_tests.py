# from .tests.tests_beginner_class import TestsBeginnerClass
# from .tests.tests_class_attendance import TestsClassAttendance
# from .tests.tests_class_registration import TestsClassRegistration
# from .tests.tests_costs import TestsCosts
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
from .tests.tests_unregister import TestsUnregisterStudent
# import json
# import logging
# import time
# import uuid
# from django.db.models import Q
# from django.test import TestCase, Client
# from django.urls import reverse
#
# from .src import SquareHelper
# from .models import BeginnerClass, ClassRegistration, Student, StudentFamily, PaymentLog, User
#
# logger = logging.getLogger(__name__)
#
#
# class TestsTemp(TestCase):
#     fixtures = ['f1']
#
#     def setUp(self):
#         # Every test needs a client.
#         self.client = Client()
#         self.test_user = User.objects.get(pk=1)
#         self.client.force_login(self.test_user)
#
#     def get_index(self):
#         # Get the page, if not super or board, page is forbidden
#         response = self.client.get(reverse('registration:index'), secure=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('student_app/index.html')
#
#     def test_square_helper_refund_payment(self):
#         sh = SquareHelper()
#         square_response = sh.comp_response('testing', 1000)
#         sh.log_payment(request, square_response, create_date=datetime.now())
