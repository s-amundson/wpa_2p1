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

    def test_update_student_family(self):
        self.client.force_login(self.test_user)
        # add a student family
        d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_register'), d, secure=True)
        sf = StudentFamily.objects.all()
        self.assertEquals(len(sf), 1)
        d['city'] = 'smallville'
        response = self.client.post(reverse('registration:student_family_api', kwargs={'family_id': 1}), d, secure=True)
        sf = StudentFamily.objects.all()
        self.assertEquals(len(sf), 1)

    def test_add_student(self):
        self.client.force_login(self.test_user)
        d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_register'), d, secure=True)

        # add a student
        response = self.client.get(reverse('registration:add_student'), secure=True)
        self.assertEqual(response.status_code, 200)
        d = {'first_name':'Christy', 'last_name': 'Smith', 'dob': '2020-02-02'}
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        # self.assertEqual(response.status_code, 200)
        sf = StudentFamily.objects.all()
        s = sf[0].student_set.all()
        self.assertEquals(len(s), 1)

        #update the record
        d['first_name'] = 'Chris'
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': 1}),  d, secure=True)
        sf = StudentFamily.objects.all()
        s = sf[0].student_set.all()
        self.assertEquals(len(s), 1)
        self.assertEqual(s[0].first_name, 'Chris')

        # check that when we get a page with a student the student shows up.
        response = self.client.get(reverse('registration:add_student', kwargs={'student_id': 1}), secure=True)
        self.assertContains(response, 'Chris')

    def test_add_student_error(self):
        self.client.force_login(self.test_user)
        d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_register'), d, secure=True)

        # add student with error
        d = {'first_name': 'Tom', 'last_name': 'Smith', 'dob': '2020/02/02'}
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        sf = StudentFamily.objects.all()
        s = sf[0].student_set.all()
        self.assertEquals(len(s), 0)
        self.assertEqual(response.status_code, 200)
        logging.debug(response.status_code)

        # go back to student family registration
        response = self.client.get(reverse('registration:student_register'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '123 main')

    def test_add_student_api(self):

        self.client.force_login(self.test_user)
        d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_register'), d, secure=True)

        # add a student
        # response = self.client.get(reverse('registration:add_student'), secure=True)
        # self.assertEqual(response.status_code, 200)
        d = {'first_name':'Christy', 'last_name': 'Smith', 'dob': '2020-02-02'}
        response = self.client.post(reverse('registration:student_api'), d, secure=True)
        # self.assertEqual(response.status_code, 200)
        sf = StudentFamily.objects.all()
        s = sf[0].student_set.all()
        self.assertEquals(len(s), 1)

