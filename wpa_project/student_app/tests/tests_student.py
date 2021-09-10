import logging
import json
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Student,  User

logger = logging.getLogger(__name__)


class TestsStudentAPI(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_student(self):
        response = self.client.get(reverse('registration:student_api'), secure=True)
        self.assertEqual(response.status_code, 200)
        d = { "first_name": "", "last_name": "", "dob": None}
        content = json.loads(response.content)
        logging.debug(content)
        for k,v in d.items():
            logging.debug(k)
            self.assertEqual(content[k], v)

    def test_get_student_id(self):
        response = self.client.get(reverse('registration:student_api', kwargs={'student_id': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        d = { "first_name": "Emily", "last_name": "Conlan", "dob": "1995-12-03"}
        content = json.loads(response.content)
        for k,v in d.items():
            self.assertEqual(content[k], v)

    def test_get_student_id_not_authorized(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:student_api', kwargs={'student_id': 1}), secure=True)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        logging.debug(content)
        self.assertEqual(content['error'], 'Not Authorized')

    def test_post_new_student(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:student_api'), d, secure=True)
        student = Student.objects.get(pk=7)
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])

    def test_post_student_id(self):
        self.test_user = User.objects.get(pk=5)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:student_api', kwargs={'student_id': 6}), d, secure=True)
        student = Student.objects.get(pk=6)
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])

    def test_post_student_id_staff(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:student_api', kwargs={'student_id': 6}), d, secure=True)
        student = Student.objects.get(pk=6)
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])

    def test_post_student_id_invalid(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Wells", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:student_api', kwargs={'student_id': 1}), d, secure=True)
        self.assertEqual(response.status_code, 404)
        student = Student.objects.get(pk=1)
        self.assertNotEqual(student.first_name, d['first_name'])
        self.assertNotEqual(student.last_name, d['last_name'])

    def test_post_student_errors(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Wells", }
        response = self.client.post(reverse('registration:student_api'), d, secure=True)
        self.assertEqual(response.status_code, 400)
        student = Student.objects.all()
        self.assertEqual(len(student), 6)

class TestsStudent(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_student(self):
        response = self.client.get(reverse('registration:add_student'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student.html')

    def test_get_student_id(self):
        response = self.client.get(reverse('registration:add_student', kwargs={'student_id': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student.html')

    def test_get_student_id_not_authorized(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:add_student', kwargs={'student_id': 1}), secure=True)
        self.assertEqual(response.status_code, 404)

    def test_post_new_student(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        logging.debug(len(Student.objects.all()))
        student = Student.objects.get(pk=7)
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])

    def test_post_student_id(self):
        self.test_user = User.objects.get(pk=5)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': 6}), d, secure=True)
        student = Student.objects.get(pk=6)
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])

    def test_post_student_id_staff(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': 6}), d, secure=True)
        student = Student.objects.get(pk=6)
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])

    def test_post_student_id_invalid(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Wells", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': 1}), d, secure=True)
        self.assertEqual(response.status_code, 404)
        student = Student.objects.get(pk=1)
        self.assertNotEqual(student.first_name, d['first_name'])
        self.assertNotEqual(student.last_name, d['last_name'])

    def test_post_student_errors(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Wells", }
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        self.assertEqual(response.status_code, 200)
        student = Student.objects.all()
        self.assertEqual(len(student), 6)

    def test_get_student_table(self):
        response = self.client.get(reverse('registration:student_table'), secure=True)
        self.assertEqual(response.status_code, 200)

