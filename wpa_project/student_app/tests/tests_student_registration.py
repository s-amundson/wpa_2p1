import logging

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib import auth

from ..models import StudentFamily, User

logger = logging.getLogger(__name__)


class TestsRegisterStudent(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User(email='ChristyCSnow@gustr.com', first_name='Christy',
                              last_name='Snow', is_active=True)
        self.test_user.set_password('password')
        self.test_user.save()
        logging.debug('here')

    def test_login_required(self):
        def get_page(page, target):
            response = self.client.get(reverse(page), secure=True)
            # self.assertRedirects(response, f'/accounts/login/?next=/{target}')
            self.assertTemplateUsed(f'student_app/{target}')


        get_page('registration:profile', 'profile.html')
        get_page('registration:student_register', 'register.html')
        get_page('registration:add_student', 'student.html')

    def test_register(self):
        # if student hasn't registered. we need to send them to registration starting with address
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:profile'), secure=True)
        # self.assertRedirects(response, reverse('registration:student_register'))
        self.assertTemplateUsed('student_app/register.html')

        response = self.client.get(reverse('registration:student_register'), secure=True)
        self.assertEqual(response.status_code, 200)

        # add a student family with error
        d = {'street': '123 main', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_register'), d, secure=True)
        self.assertTemplateUsed('student_app/register.html')
        self.assertEqual(response.status_code, 200)
        sf = StudentFamily.objects.all()
        self.assertEquals(len(sf), 0)


        # add a student family
        d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_register'), d, secure=True)
        self.assertTemplateUsed('student_app/profile.html')
        # self.assertRedirects(response, reverse('registration:profile'))
        self.assertTemplateUsed('student_app/profile.html')
        sf = StudentFamily.objects.all()
        self.assertEquals(len(sf), 1)

        # check that we can go back to profile.
        response = self.client.get(reverse('registration:profile'), secure=True)
        self.assertEqual(response.status_code, 200)

        # add a student
        response = self.client.get(reverse('registration:add_student'), secure=True)
        self.assertEqual(response.status_code, 200)
        d = {'first_name':'Christy', 'last_name': 'Smith', 'dob': '2020-02-02'}
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        # self.assertEqual(response.status_code, 200)
        s = sf[0].student_set.all()
        self.assertEquals(len(s), 1)

        # check that when we get a page with a student the student shows up.
        response = self.client.get(reverse('registration:add_student', kwargs={'student_id': 1}), secure=True)
        self.assertContains(response, 'Christy')

        # add student with error
        d = {'first_name': 'Tom', 'last_name': 'Smith', 'dob': '2020/02/02'}
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        s = sf[0].student_set.all()
        self.assertEquals(len(s), 1)
        self.assertEqual(response.status_code, 200)
        logging.debug(response.status_code)

        # go back to student family registration
        response = self.client.get(reverse('registration:student_register'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '123 main')


    def test_login_invaid(self):
        """Tests invalid login with username and password"""
        response = self.client.post(reverse('account_login'), {'login': 'john', 'password': 'smith'}, secure=True)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
        self.assertTemplateUsed('account/login.html')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_login'), {'login': 'john@smith.com', 'password': 'smith'}, secure=True)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
        self.assertTemplateUsed('account/login.html')
        self.assertEqual(response.status_code, 200)
        # self.assertRedirects(reverse('account_login'))
        # with :
        #     render_to_string('account/login.html')
        logging.debug(response)
