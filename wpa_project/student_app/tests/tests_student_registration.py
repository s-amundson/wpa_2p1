import logging
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Student, StudentFamily, User

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
            self.assertTemplateUsed(f'student_app/{target}')

        get_page('registration:profile', 'profile.html')
        get_page('registration:student_register', 'register.html')
        get_page('registration:add_student', 'student.html')

    def test_register(self):
        s = Student(first_name="Emily", last_name="Conlan", dob="1995-12-03", safety_class=None, user=self.test_user)
        s.save()
        # if student hasn't registered. we need to send them to registration starting with address
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:profile'), secure=True)
        self.assertTemplateUsed('student_app/register.html')

        response = self.client.get(reverse('registration:student_register'), secure=True)
        self.assertEqual(response.status_code, 200)

        # add a student family with error
        d = {'street': '123 main', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_family_api'), d, secure=True)
        # self.assertTemplateUsed('student_app/register.html')
        self.assertEqual(response.status_code, 400)
        sf = StudentFamily.objects.all()
        self.assertEquals(len(sf), 0)

        # add a student family
        d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_family_api'), d, secure=True)
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
        s = Student(first_name="Emily", last_name="Conlan", dob="1995-12-03", safety_class=None, user=self.test_user)
        s.save()
        # add a student family
        d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_family_api'), d, secure=True)
        sf = StudentFamily.objects.all()
        self.assertEquals(len(sf), 1)
        logging.debug(sf.values())
        d['city'] = 'smallville'
        response = self.client.post(reverse('registration:student_family_api', kwargs={'family_id': 1}), d, secure=True)
        sf = StudentFamily.objects.all()
        self.assertEquals(len(sf), 1)

    def test_add_student(self):
        self.client.force_login(self.test_user)
        # d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        # response = self.client.post(reverse('registration:student_family_api'), d, secure=True)
        sf = StudentFamily.objects.create(street='123 main', city='city', state='ca', post_code=12345,
                                          phone='123.123.1234')
        sf.save()
        # sf.user.add(self.test_user)
        # sf.save()

        student = Student(student_family=sf, first_name='Christy', last_name='Smith', dob='2020-02-02',
                          user=self.test_user)
        student.save()
        logging.debug(student.id)

        # update the record
        d = {'first_name': 'Chris', 'last_name': 'Smith', 'dob': '2020-02-02'}
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': student.id}), d,
                                    secure=True)
        sf = StudentFamily.objects.all()
        s = sf[0].student_set.all()
        self.assertEquals(len(s), 1)
        self.assertEqual(s[0].first_name, 'Chris')

        # check that when we get a page with a student the student shows up.
        response = self.client.get(reverse('registration:add_student', kwargs={'student_id': student.id}), secure=True)
        self.assertContains(response, 'Chris')

    def test_add_student_error(self):
        student = Student(student_family=None, first_name='Christy', last_name='Smith', dob='2020-02-02',
                          user=self.test_user)
        student.save()
        self.client.force_login(self.test_user)
        d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_family_api'), d, secure=True)

        # add student with error
        d = {'first_name': 'Tom', 'last_name': 'Smith', 'dob': '2020/02/02'}
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        sf = StudentFamily.objects.all()
        s = sf[0].student_set.all()
        self.assertEquals(len(s), 1)
        self.assertEqual(response.status_code, 200)
        logging.debug(response.status_code)

        # go back to student family registration
        response = self.client.get(reverse('registration:student_register'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '123 main')

