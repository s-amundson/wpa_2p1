import logging
import json
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib import auth
from django.utils import timezone

from event.models import Event, Registration
from ..models import Student, StudentFamily,  User

logger = logging.getLogger(__name__)

# @tag('temp')
class TestsStudentFamily(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_student_family(self):
        response = self.client.get(reverse('registration:student_family'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student_family_form.html')

    # @tag('temp')
    def test_get_student_family_id(self):
        response = self.client.get(reverse('registration:student_family', kwargs={'family_id': 2}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student_family_form.html')

    def test_get_student_family_id_own_family(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:student_family', kwargs={'family_id': 2}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student_family_form.html')

    def test_get_student_family_id_unauthorized(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:student_family', kwargs={'family_id': 2}), secure=True)
        # self.assertEqual(response.status_code, 400)
        self.assertEqual(response.status_code, 404)

    # @tag('temp')
    def test_get_student_family_id_staff(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:student_family', kwargs={'family_id': 4}), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_post_student_family_exists(self):
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family'), d, secure=True)
        self.assertRedirects(response, reverse('registration:profile'))
        sf = StudentFamily.objects.get(pk=1)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])
        self.assertEqual(self.test_user.student_set.last().student_family, sf)

    def test_post_student_family_exists_json(self):
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family'), d, secure=True,
                                    HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        for k,v in d.items():
            self.assertEqual(content[k], v)
        sf = StudentFamily.objects.get(pk=1)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])
        self.assertEqual(self.test_user.student_set.last().student_family, sf)

    def test_post_student_family_not_exists(self):
        s = Student.objects.get(pk=6)
        s.student_family = None
        s.save()

        self.test_user = User.objects.get(pk=5)
        self.client.force_login(self.test_user)
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family'), d, secure=True)
        self.assertRedirects(response, reverse('registration:profile'))
        sf = StudentFamily.objects.get(pk=5)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])

    def test_post_student_family_not_exists_json(self):
        s = Student.objects.get(pk=6)
        s.student_family = None
        s.save()

        self.test_user = User.objects.get(pk=5)
        self.client.force_login(self.test_user)
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family'), d, secure=True,
                                    HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        for k, v in d.items():
            self.assertEqual(content[k], v)
        sf = StudentFamily.objects.get(pk=5)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])

    def test_post_student_family_id_staff(self):
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family', kwargs={'family_id': 2}), d, secure=True)
        self.assertRedirects(response, reverse('registration:profile'))
        sf = StudentFamily.objects.get(pk=2)
        self.assertEqual(sf.street, d['street'])
        self.assertEqual(sf.city, d['city'])
        self.assertEqual(sf.state, d['state'])

    def test_post_student_family_id_staff_json(self):
        d = {"street": "1948 Jones Avenue", "city": "Bays", "state": "NC",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family', kwargs={'family_id': 2}), d, secure=True,
                                    HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
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
        response = self.client.post(reverse('registration:student_family', kwargs={'family_id': 2}), d, secure=True)
        self.assertEqual(response.status_code, 404)

        sf = StudentFamily.objects.get(pk=2)
        self.assertNotEqual(sf.street, d['street'])
        self.assertNotEqual(sf.city, d['city'])
        self.assertNotEqual(sf.state, d['state'])

    def test_post_student_error(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        d = {"street": "1948 Jones Avenue", "city": "Bays",
         "post_code": "28636", "phone": "336-696-6307"}
        response = self.client.post(reverse('registration:student_family', kwargs={'family_id': 2}), d, secure=True)
        self.assertEqual(response.status_code, 200)

        sf = StudentFamily.objects.get(pk=2)
        self.assertNotEqual(sf.street, d['street'])
        self.assertNotEqual(sf.city, d['city'])

    def test_phone_feild(self):
        from ..fields import PhoneField
        sf = StudentFamily.objects.get(pk=2)
        pf = PhoneField()
        self.assertIsNone(pf.to_python(None))

    def test_student_family_delete_get_super(self):
        response = self.client.get(reverse('registration:delete_student_family', kwargs={'pk': 3}), secure=True)
        self.assertTemplateUsed('student_app/delete.html')
        self.assertEqual(response.status_code, 200)

    def test_student_family_delete_get_valid(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:delete_student_family', kwargs={'pk': 3}), secure=True)
        self.assertTemplateUsed('student_app/delete.html')
        self.assertEqual(response.status_code, 200)

    def test_post_delete_student_family(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('registration:delete_student_family', kwargs={'pk': 3}),
                                    {'delete': 'delete', 'pk': 3}, secure=True)
        self.assertRedirects(response, reverse('registration:index'))
        students = Student.objects.all()
        self.assertEqual(len(students), 4)
        self.assertEqual(len(students.filter(pk=4)), 0)
        self.assertEqual(len(students.filter(pk=5)), 0)
        sf = StudentFamily.objects.all()
        self.assertEqual(len(sf), 3)
        self.assertEqual(len(sf.filter(pk=3)), 0)
        users = User.objects.all()
        self.assertEqual(len(users), 3)
        self.assertEqual(len(users.filter(pk=3)), 0)
        assert not auth.get_user(self.client).is_authenticated

    def test_post_delete_student_family_invalid(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('registration:delete_student_family', kwargs={'pk': 2}),
                                    {'delete': 'delete', 'pk': 2}, secure=True)
        students = Student.objects.all()
        self.assertEqual(len(students), 6)
        sf = StudentFamily.objects.all()
        self.assertEqual(len(sf), 4)
        users = User.objects.all()
        self.assertEqual(len(users), 5)
        assert auth.get_user(self.client).is_authenticated

    def test_post_delete_student_family_registrations(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        cr = Registration.objects.create(
            event=Event.objects.create(
                event_date=timezone.now() + timezone.timedelta(days=4),
                state='open',
                type='class',
            ),
            student=Student.objects.get(pk=3),
            pay_status="paid",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)

        response = self.client.post(reverse('registration:delete_student_family', kwargs={'pk': 2}),
                                    {'delete': 'delete', 'pk': 2}, secure=True)
        students = Student.objects.all()
        self.assertEqual(len(students), 6)
        sf = StudentFamily.objects.all()
        self.assertEqual(len(sf), 4)
        users = User.objects.all()
        self.assertEqual(len(users), 5)
        assert auth.get_user(self.client).is_authenticated

    # @tag("temp")
    def test_post_delete_student_family_super(self):
        # self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('registration:delete_student_family', kwargs={'pk': 3}),
                                    {'delete': 'delete', 'pk': 3}, secure=True)
        self.assertRedirects(response, reverse('registration:index'))
        students = Student.objects.all()
        self.assertEqual(len(students), 4)
        self.assertEqual(len(students.filter(pk=4)), 0)
        self.assertEqual(len(students.filter(pk=5)), 0)
        sf = StudentFamily.objects.all()
        self.assertEqual(len(sf), 3)
        self.assertEqual(len(sf.filter(pk=3)), 0)
        users = User.objects.all()
        self.assertEqual(len(users), 3)
        self.assertEqual(len(users.filter(pk=3)), 0)
        self.assertEqual(len(users.filter(pk=1)), 1)
        assert auth.get_user(self.client).is_authenticated