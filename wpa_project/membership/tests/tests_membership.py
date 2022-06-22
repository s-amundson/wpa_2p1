import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps
from django.utils import timezone
from datetime import timedelta

from ..models import Level, Membership, Member
from student_app.models import Student
logger = logging.getLogger(__name__)


class TestsMembership(TestCase):
    fixtures = ['f1', 'level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)

    def test_membership_get_page(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('membership:membership'), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_membership_to_old(self):
        response = self.client.post(reverse('membership:membership'), {'student_2': 'on', 'level': '2'},
                                    secure=True)
        # self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

    def test_membership_good(self):
        response = self.client.post(reverse('membership:membership'), {'student_2': 'on', 'level': '1'},
                                    secure=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(self.client.session['payment_db'][1], 'Membership')

    def test_membership_to_young(self):
        s = Student.objects.get(pk=2)
        s.dob = "2011-07-22"
        s.save()

        response = self.client.post(reverse('membership:membership'), {'student_2': 'on', 'level': '1'},
                                    secure=True)
        # self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

    def test_membership_family(self):
        response = self.client.post(reverse('membership:membership'), {'student_2': 'on', 'student_3': 'on', 'level': '3'},
                                    secure=True)
        # self.assertEqual(response.status_code, 200)

    def test_membership_family_large(self):
        students = Student.objects.filter(pk__gt=1)
        sf = students[0].student_family
        for s in students:
            s.student_family = sf;
            s.save()

        d = {'student_2': 'on', 'student_3': 'on', 'student_4': 'on', 'student_5': 'on', 'student_6': 'on', 'level': '3'}
        response = self.client.post(reverse('membership:membership'), d, secure=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(self.client.session['payment_db'][1], 'Membership')
        self.assertEqual(self.client.session['line_items'][0]['amount_each'], 50)
        self.assertEqual(len(Membership.objects.all()), 1)
        self.assertEqual(Membership.objects.last().students.count(), 5)

    def test_membership_no_student(self):
        response = self.client.post(reverse('membership:membership'), {'level': '3'}, secure=True)
        # self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

    def test_membership_multiple_not_family(self):
        response = self.client.post(reverse('membership:membership'), {'student_2': 'on', 'student_3': 'on', 'level': '1'},
                                    secure=True)
        # self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(len(Membership.objects.all()), 0)

    def test_get_student_table(self):
        d_now = timezone.localtime(timezone.now()).date()
        student = Student.objects.get(pk=2)
        student.user.is_member = True
        student.user.save()
        member = Member.objects.create(student=student, expire_date=d_now + timedelta(days=30),
                                       level=Level.objects.get(pk=1), join_date=d_now - timedelta(days=600))
        member.save()
        response = self.client.get(reverse('registration:student_table'), secure=True)
        self.assertEqual(response.status_code, 200)
