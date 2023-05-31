import logging
import random

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from student_app.models import Student
from ..models import Session, Registration

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadRegistration(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.student_dict = {'session': 1, 'student_8': True}

    def set_joad_age(self, student, age=None):
        if age is None:
            age = random.randint(10, 19)
        dob = student.dob
        birth = timezone.now().date()
        student.dob = birth.replace(year=birth.year - age, month=dob.month, day=dob.day)
        student.save()

    def test_no_user_get(self):
        response = self.client.get(reverse('joad:registration'), secure=True)
        self.assertEqual(response.status_code, 302)

    def test_no_student_family_get(self):
        student = Student.objects.get(pk=4)
        student.student_family = None
        student.save()
        self.client.force_login(student.user)
        response = self.client.get(reverse('joad:registration'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_user_normal_get_no_student(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:registration'), secure=True)
        self.assertEqual(response.context['form'].student_count, 0)
        self.assertTemplateUsed(response, 'joad/registration.html')
        self.assertEqual(response.status_code, 200)

    def test_staff_user_get(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:registration'), secure=True)
        self.assertEqual(response.context['form'].student_count, 4)
        self.assertTemplateUsed(response, 'joad/registration.html')
        self.assertEqual(response.status_code, 200)

    def test_staff_user_get_existing(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:registration', kwargs={'session_id': 1}), secure=True)
        self.assertEqual(response.context['form'].student_count, 4)
        self.assertTemplateUsed(response, 'joad/registration.html')
        self.assertEqual(response.status_code, 200)

    def test_staff_post(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:registration'), self.student_dict, secure=True)
        logger.debug(self.client.session['line_items'][0]['name'])
        self.assertEqual(self.client.session['line_items'][0]['name'], 'Joad session starting 2022-02-01 student id: 8')
        self.assertEqual(self.client.session['payment_description'], 'Joad session starting 2022-02-01')
        self.assertEqual(self.client.session['payment_category'], 'joad')

    def test_user_post_good(self):
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:registration'), self.student_dict, secure=True)
        logger.debug(self.client.session['line_items'][0]['name'])
        self.assertEqual(self.client.session['line_items'][0]['name'], 'Joad session starting 2022-02-01 student id: 8')
        self.assertEqual(self.client.session['payment_description'], 'Joad session starting 2022-02-01')
        self.assertEqual(self.client.session['payment_category'], 'joad')

    def test_user_post_bad(self):
        self.test_user = User.objects.get(pk=5)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:registration'), self.student_dict, secure=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid student selected')
        self.assertEqual(response.status_code, 200)

    def test_class_full(self):
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)
        session = Session.objects.get(pk=1)
        session.student_limit = 1
        session.save()
        registration = Registration(pay_status='paid',
                                    idempotency_key='992c77a8-87cc-45af-b390-13d80554e3e0',
                                    student=Student.objects.get(pk=9),
                                    session=session)
        registration.save()

        response = self.client.post(reverse('joad:registration'), self.student_dict, secure=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Class is full')
        self.assertEqual(response.status_code, 200)

    def test_student_registered(self):
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)
        session = Session.objects.get(pk=1)
        registration = Registration(pay_status='paid',
                                    idempotency_key='992c77a8-87cc-45af-b390-13d80554e3e0',
                                    student=Student.objects.get(pk=8),
                                    session=session)
        registration.save()

        response = self.client.post(reverse('joad:registration'), self.student_dict, secure=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Student is already enrolled')
        self.assertEqual(response.status_code, 200)

    def test_session_wrong_state(self):
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)
        session = Session.objects.get(pk=1)
        session.state = 'closed'
        session.save()

        response = self.client.post(reverse('joad:registration'), self.student_dict, secure=True)
        form = response.context['form']
        self.assertIn('session', form.errors.keys())
        self.assertIn('Select a valid choice. That choice is not one of the available choices.', form.errors['session'])

    def test_user_post_young(self):
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)
        student = Student.objects.get(pk=8)
        self.set_joad_age(student, 7)

        response = self.client.post(reverse('joad:registration'), self.student_dict, secure=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Student is to young')
        self.assertEqual(response.status_code, 200)

    def test_user_post_old(self):
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)
        student = Student.objects.get(pk=8)
        self.set_joad_age(student, 22)

        response = self.client.post(reverse('joad:registration'), self.student_dict, secure=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        # form limits students to joad age therefor 'Student is to old' doesn't execute
        self.assertEqual(str(messages[0]), 'Invalid student selected')
        self.assertEqual(response.status_code, 200)

    def test_student_resume_register(self):
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)
        session = Session.objects.get(pk=1)
        registration = Registration(pay_status='start',
                                    idempotency_key='992c77a8-87cc-45af-b390-13d80554e3e0',
                                    student=Student.objects.get(pk=8),
                                    session=session)
        registration.save()

        response = self.client.get(reverse('joad:resume_registration', kwargs={'reg_id': registration.id}),
                                    self.student_dict, secure=True)
        logger.debug(self.client.session['line_items'][0]['name'])
        self.assertEqual(self.client.session['payment_description'], 'Joad session starting 2022-02-01')
        self.assertEqual(self.client.session['payment_category'], 'joad')
