# from .tests.tests_covid_vax import TestsCovidVax
# from .tests.tests_email import TestsEmail
# from .tests.tests_index import TestsIndex
# from .tests.tests_instructor import TestsInstructor
# from .tests.tests_other import TestsOther
# from .tests.tests_pdf import TestsPdf
# from .tests.tests_search import TestsSearch
# from .tests.tests_student import TestsStudent
# from .tests.tests_student import TestsStudentAPI
# from .tests.tests_student_family import TestsStudentFamily
# from .tests.tests_student_family import TestsStudentFamilyAPI
# from .tests.tests_student_list import TestsSearchList
# from .tests.tests_student_registration import TestsRegisterStudent
# from .tests.tests_theme import TestsTheme


# import logging
# import json
# from django.core import mail
# from django.test import TestCase, Client
# from django.urls import reverse
#
# from .src import EmailMessage
# from .models import Student, User
#
# logger = logging.getLogger(__name__)
#
#
# class TestsStudentAPI(TestCase):
#     fixtures = ['f1']
#
#     def setUp(self):
#         # Every test needs a client.
#         self.client = Client()
#
#     def test_bcc(self):
#         students = Student.objects.all()
#         em = EmailMessage()
#         em.bcc_from_students(students)
