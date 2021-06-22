import logging
import json
from django.test import TestCase, Client
from django.urls import reverse

from ..models import StudentFamily,  User

logger = logging.getLogger(__name__)


class TestsStudentFamily(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.url_string = 'registration:student_register'

    def test_get_student_family(self):
        response = self.client.get(reverse(self.url_string), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student_family_form.html')

    def test_get_student_family_id(self):
        response = self.client.get(reverse(self.url_string, kwargs={'family_id': 2}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student_family_form.html')

    def test_get_student_family_id_unauthorized(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse(self.url_string, kwargs={'family_id': 2}), secure=True)
        self.assertEqual(response.status_code, 404)

    def test_get_student_family_id_staff(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse(self.url_string, kwargs={'family_id': 4}), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_post_student_family_exists(self):
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse(self.url_string), d, secure=True)
        self.assertEqual(response.status_code, 302)

        sf = StudentFamily.objects.get(pk=1)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])

    def test_post_student_family_not_exists(self):
        self.test_user = User.objects.get(pk=5)
        self.client.force_login(self.test_user)
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse(self.url_string), d, secure=True)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        logging.debug(content)
        for k,v in d.items():
            self.assertEqual(content[k], v)
        sf = StudentFamily.objects.get(pk=5)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])

    def test_post_student_family_id_staff(self):
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse(self.url_string, kwargs={'family_id': 2}), d, secure=True)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        logging.debug(content)
        for k,v in d.items():
            self.assertEqual(content[k], v)
        sf = StudentFamily.objects.get(pk=2)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])


    def test_post_student_unauthorized(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse(self.url_string, kwargs={'family_id': 2}), d, secure=True)
        self.assertEqual(response.status_code, 400)

        sf = StudentFamily.objects.get(pk=2)
        self.assertNotEqual(sf.street, d['street'])
        self.assertNotEqual(sf.city, d['city'])
        self.assertNotEqual(sf.state, d['state'])


class TestsStudentFamilyAPI(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_student_family(self):
        response = self.client.get(reverse('registration:student_family_api'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student_family_form.html')

    def test_get_student_family_id(self):
        response = self.client.get(reverse('registration:student_family_api', kwargs={'family_id': 2}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student_family_form.html')

    def test_get_student_family_id_own_family(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:student_family_api', kwargs={'family_id': 2}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student_family_form.html')

    def test_get_student_family_id_unauthorized(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:student_family_api', kwargs={'family_id': 2}), secure=True)
        self.assertEqual(response.status_code, 400)

    def test_get_student_family_id_staff(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:student_family_api', kwargs={'family_id': 4}), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_post_student_family_exists(self):
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family_api'), d, secure=True)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        logging.debug(content)
        for k,v in d.items():
            self.assertEqual(content[k], v)
        sf = StudentFamily.objects.get(pk=1)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])

    def test_post_student_family_not_exists(self):
        self.test_user = User.objects.get(pk=5)
        self.client.force_login(self.test_user)
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family_api'), d, secure=True)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        logging.debug(content)
        for k,v in d.items():
            self.assertEqual(content[k], v)
        sf = StudentFamily.objects.get(pk=5)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])

    def test_post_student_family_id_staff(self):
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family_api', kwargs={'family_id': 2}), d, secure=True)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        logging.debug(content)
        for k,v in d.items():
            self.assertEqual(content[k], v)
        sf = StudentFamily.objects.get(pk=2)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])


    def test_post_student_unauthorized(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family_api', kwargs={'family_id': 2}), d, secure=True)
        self.assertEqual(response.status_code, 400)

        sf = StudentFamily.objects.get(pk=2)
        self.assertNotEqual(sf.street, d['street'])
        self.assertNotEqual(sf.city, d['city'])
        self.assertNotEqual(sf.state, d['state'])

    def test_post_student_error(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        d = {"street": "1948 Jones Avenue", "city": "Bays",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family_api', kwargs={'family_id': 2}), d, secure=True)
        self.assertEqual(response.status_code, 400)

        sf = StudentFamily.objects.get(pk=2)
        self.assertNotEqual(sf.street, d['street'])
        self.assertNotEqual(sf.city, d['city'])


    def test_phone_feild(self):
        from ..fields import PhoneField
        sf = StudentFamily.objects.get(pk=2)
        pf = PhoneField()
        self.assertIsNone(pf.to_python(None))
