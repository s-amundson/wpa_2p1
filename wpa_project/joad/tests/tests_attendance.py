import logging
import json
from django.apps import apps
from django.test import TestCase, Client, tag
from django.urls import reverse

from student_app.models import Student
from ..models import Attendance, JoadClass

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadAttendance(TestCase):
    fixtures = ['f1', 'joad1', 'joad_registration']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.student_dict = {'session': 1, 'student_8': True}

    def test_user_normal_get(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:attendance'), secure=True)
        self.assertEqual(response.status_code, 403)

    # @tag('temp')
    def test_staff_user_get_no_class(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:attendance'), secure=True)
        self.assertEqual(response.status_code, 404)

    # @tag('temp')
    def test_staff_user_get(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:attendance', kwargs={'class_id': 1}), secure=True)
        self.assertEqual(len(response.context['object_list']), 4)
        self.assertTemplateUsed(response, 'joad/attendance.html')

    # @tag('temp')
    def test_staff_user_get_attended(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)

        jc = JoadClass.objects.get(pk=1)
        student = Student.objects.get(pk=8)
        a = Attendance(joad_class=jc, student=student, attended=True)
        a.save()

        response = self.client.get(reverse('joad:attendance', kwargs={'class_id': 1}), secure=True)
        self.assertEqual(len(response.context['object_list']), 4)
        self.assertTemplateUsed(response, 'joad/attendance.html')

    def test_user_normal_post(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:attend', kwargs={'class_id': 1}), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_staff_user_post_attend(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:attend', kwargs={'class_id': 1}), {'check_8': True}, secure=True)
        a = Attendance.objects.all()
        logger.debug(a)
        self.assertEqual(len(a), 1)
        self.assertTrue(a[0].attended)

    def test_staff_user_post_unattend(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        jc = JoadClass.objects.get(pk=1)
        student = Student.objects.get(pk=8)
        a = Attendance(joad_class=jc, student=student, attended=True)
        a.save()

        response = self.client.post(reverse('joad:attend', kwargs={'class_id': 1}), {'check_8': False}, secure=True)
        a = Attendance.objects.all()
        logger.debug(a)
        self.assertEqual(len(a), 1)
        self.assertFalse(a[0].attended)

    def test_staff_user_post_attend_error(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:attend', kwargs={'class_id': 1}), {}, secure=True)
        a = Attendance.objects.all()
        logger.debug(a)
        self.assertEqual(len(a), 0)
        content = json.loads(response.content)
        logger.debug(content)
        self.assertFalse(content['attend'])
        self.assertTrue(content['error'])
