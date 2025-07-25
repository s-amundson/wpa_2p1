import logging
import json
from django.core import mail
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.utils import timezone
from allauth.account.models import EmailAddress

from ..models import Student, User
from event.models import Event, Registration

logger = logging.getLogger(__name__)


# @tag('temp')
class TestsStudent(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    # @tag("temp")
    def test_get_student(self):
        response = self.client.get(reverse('registration:add_student'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student.html')

    # @tag("temp")
    def test_get_student_id(self):
        response = self.client.get(reverse('registration:add_student', kwargs={'student_id': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student.html')

    # @tag("temp")
    def test_get_student_id_not_staff(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:add_student', kwargs={'student_id': 5}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/student.html')

    # @tag("temp")
    def test_get_student_id_not_authorized(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:add_student', kwargs={'student_id': 1}), secure=True)
        self.assertEqual(response.status_code, 404)

    # @tag("temp")
    def test_post_add_student(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        student = Student.objects.last()
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])
        self.assertEqual(student.student_family, self.test_user.student_set.last().student_family)
        self.assertEqual(len(mail.outbox), 0)

    # @tag("temp")
    def test_post_add_student_no_address(self):
        self.test_user = User.objects.get(pk=4)
        s = self.test_user.student_set.last()
        s.student_family = None
        s.save()
        logging.warning(self.test_user.student_set.last().student_family)
        self.client.force_login(self.test_user)

        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        self.assertEqual(response.status_code, 302)
        student = Student.objects.last()
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])
        # self.assertEqual(student.student_family, self.test_user.student_set.last().student_family)
        self.assertEqual(len(mail.outbox), 0)

    # @tag("temp")
    def test_post_add_student_json(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:add_student'), d, secure=True, HTTP_ACCEPT='application/json')
        student = Student.objects.last()
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])
        self.assertEqual(student.student_family, self.test_user.student_set.last().student_family)
        self.assertEqual(len(mail.outbox), 0)
        content = json.loads(response.content)
        self.assertEqual(content['first_name'], "Kiley")

    # @tag("temp")
    def test_post_student_id(self):
        self.test_user = User.objects.get(pk=5)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': 6}), d, secure=True)
        student = Student.objects.get(pk=6)
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])
        self.assertEqual(len(mail.outbox), 0)

    # @tag("temp")
    def test_post_student_id_staff(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03", "is_staff": "on"}
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': 6}), d, secure=True)
        student = Student.objects.get(pk=6)
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(student.student_family.id, 4)


    # @tag("temp")
    def test_post_student_id_invalid(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Wells", "dob": "1995-12-03"}
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': 1}), d, secure=True)
        self.assertEqual(response.status_code, 404)
        student = Student.objects.get(pk=1)
        self.assertNotEqual(student.first_name, d['first_name'])
        self.assertNotEqual(student.last_name, d['last_name'])
        self.assertEqual(len(mail.outbox), 0)

    # @tag("temp")
    def test_post_student_form_invalid_json(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Wells", "dob": "1995-22-03"}
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': 5}), d, secure=True,
                                    HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        student = Student.objects.get(pk=1)
        self.assertNotEqual(student.first_name, d['first_name'])
        self.assertNotEqual(student.last_name, d['last_name'])
        self.assertEqual(len(mail.outbox), 0)
        content = json.loads(response.content)
        logging.warning(content)
        self.assertNotEqual(content['error'], {})

    # @tag("temp")
    def test_post_student_errors(self):
        self.test_user = User.objects.get(pk=4)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Wells", }
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        self.assertEqual(response.status_code, 200)
        student = Student.objects.all()
        self.assertEqual(len(student), 6)
        self.assertEqual(len(mail.outbox), 0)

    # @tag("temp")
    def test_new_user_new_student(self):
        u = User(username='testuser', email='test@example.com', password='password')
        u.save()
        self.client.force_login(u)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03", "email": "test@example.com"}
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        student = Student.objects.last()
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])
        self.assertEqual(student.email, 'test@example.com')
        self.assertEqual(len(mail.outbox), 0)

    # @tag("temp")
    def test_new_user_existing_student(self):
        self.test_user = User.objects.get(pk=5)
        self.client.force_login(self.test_user)
        d = {"first_name": "Kiley", "last_name": "Conlan", "dob": "1995-12-03", "email": "test@example.com"}
        response = self.client.post(reverse('registration:add_student'), d, secure=True)
        student = Student.objects.last()
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])
        self.assertEqual(student.email, 'test@example.com')
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Invitation')

    # @tag("temp")
    def test_add_email_existing_student(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        d = {"first_name": "Heidi", "last_name": "Hall", "dob": "1986-04-20", "email": "test@example.com"}
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': 3}), d, secure=True)
        student = Student.objects.get(pk=3)
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])
        self.assertEqual(student.email, 'test@example.com')
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Invitation')

    # @tag('temp')
    def test_modify_existing_user(self):
        self.test_user.save()
        d = {"first_name": "Charles", "last_name": "Wells", "dob": "1995-12-03", "is_instructor": True}
        response = self.client.post(reverse('registration:add_student', kwargs={'student_id': 4}), d, secure=True)
        student = Student.objects.get(pk=4)
        self.assertEqual(student.first_name, d['first_name'])
        self.assertEqual(student.last_name, d['last_name'])
        self.assertTrue(student.user.has_perm('student_app.staff'))
        self.assertTrue(student.user.has_perm('student_app.instructors'))
        self.assertTrue(student.user.is_active)

    # @tag("temp")
    def test_get_student_table(self):
        response = self.client.get(reverse('registration:student_table'), secure=True)
        self.assertEqual(response.status_code, 200)

    # @tag("temp")
    def test_student_is_joad_young(self):
        student = Student.objects.get(pk=3)
        birth = timezone.now().date()
        student.dob = birth.replace(year=birth.year - 7)
        student.save()

        response = self.client.post(reverse('registration:is_joad', kwargs={'student_id': 3}), {'joad_check_3': True},
                                    secure=True)
        content = json.loads(response.content)
        self.assertTrue(content['error'])
        self.assertEqual(content['message'], 'Student to young')

    # @tag("temp")
    def test_student_is_joad_good(self):
        student = Student.objects.get(pk=3)
        birth = timezone.now().date()
        student.dob = birth.replace(year=birth.year - 15)
        student.save()

        response = self.client.post(reverse('registration:is_joad', kwargs={'student_id': 3}), {'joad_check_3': True},
                                    secure=True)
        content = json.loads(response.content)
        self.assertFalse(content['error'])
        self.assertEqual(content['message'], '')

    # @tag("temp")
    def test_student_is_joad_old(self):
        student = Student.objects.get(pk=3)
        birth = timezone.now().date()
        student.dob = birth.replace(year=birth.year - 22)
        student.save()

        response = self.client.post(reverse('registration:is_joad', kwargs={'student_id': 3}),
                                    {'joad_check_3': True},
                                    secure=True)
        content = json.loads(response.content)
        self.assertTrue(content['error'])
        self.assertEqual(content['message'], 'Student to old')

    # @tag("temp")
    def test_get_delete_student_superuser(self):
        self.test_user.is_superuser = True
        self.test_user.save()
        response = self.client.get(reverse('registration:delete_student', kwargs={'pk': 4}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/delete.html')

    # @tag("temp")
    def test_get_delete_student_valid(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:delete_student', kwargs={'pk': 5}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/delete.html')

    # @tag('temp')
    def test_get_delete_student_invalid(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:delete_student', kwargs={'pk': 3}), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_get_delete_student_redirect(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:delete_student', kwargs={'pk': 2}), secure=True)
        self.assertRedirects(response, reverse('registration:delete_student_family', kwargs={'pk': 2}))

    # @tag("temp")
    def test_post_delete_student_superuser(self):
        self.test_user.is_superuser = True
        self.test_user.save()
        response = self.client.post(reverse('registration:delete_student', kwargs={'pk': 3}),
                                    {'delete': 'delete', 'pk': 3}, secure=True)
        self.assertRedirects(response, reverse('registration:profile'))
        students = Student.objects.all()
        self.assertEqual(len(students), 5)
        self.assertEqual(len(students.filter(pk=3)), 0)
        self.assertEqual(len(User.objects.filter(pk=1)), 1)

    def test_post_delete_student(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('registration:delete_student', kwargs={'pk': 3}),
                                    {'delete': 'delete', 'pk': 3}, secure=True)
        self.assertRedirects(response, reverse('registration:profile'))
        students = Student.objects.all()
        self.assertEqual(len(students), 5)
        self.assertEqual(len(students.filter(pk=3)), 0)

    def test_post_delete_student_with_user(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('registration:delete_student', kwargs={'pk': 5}),
                                    {'delete': 'delete', 'removal_choice': 'delete', 'pk': 5}, secure=True)
        self.assertRedirects(response, reverse('registration:profile'))
        students = Student.objects.all()
        self.assertEqual(len(students), 5)
        self.assertEqual(len(students.filter(pk=5)), 0)
        users = User.objects.all()
        self.assertEqual(len(users), 4)
        self.assertEqual(len(users.filter(pk=4)), 0)
        self.assertEqual(len(EmailAddress.objects.filter(email='RicardoRHoyt@jourrapide.com')), 0)

    def test_post_remove_student_with_user(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('registration:delete_student', kwargs={'pk': 5}),
                                    {'delete': 'delete', 'removal_choice': 'remove', 'pk': 5}, secure=True)
        self.assertRedirects(response, reverse('registration:profile'))
        students = Student.objects.all()
        self.assertEqual(len(students), 6)
        self.assertEqual(len(students.filter(pk=5)), 1)
        users = User.objects.all()
        self.assertEqual(len(users), 5)
        self.assertEqual(len(users.filter(pk=4)), 1)
        self.assertEqual(len(EmailAddress.objects.filter(email='RicardoRHoyt@jourrapide.com')), 1)
        self.assertIsNone(Student.objects.get(pk=5).student_family)

    # @tag('temp')
    def test_post_delete_invalid(self):
        self.test_user.is_superuser = True
        self.test_user.save()
        response = self.client.post(reverse('registration:delete_student', kwargs={'pk': 3}),
                                    {'delete': 'delete', 'pk': 10}, secure=True)
        self.assertContains(response, 'Form Error - Invalid Student')
        students = Student.objects.all()
        self.assertEqual(len(students), 6)
        self.assertEqual(len(students.filter(pk=3)), 1)

    def test_post_delete_student_with_registration_invalid(self):
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
        response = self.client.post(reverse('registration:delete_student', kwargs={'pk': 3}),
                                    {'delete': 'delete', 'pk': 3}, secure=True)
        logger.warning(response.context)
        # self.assertContains(response, 'Student has registrations')
        students = Student.objects.all()
        self.assertEqual(len(students), 6)
        self.assertEqual(len(students.filter(pk=3)), 1)

    def test_post_delete_student_with_registration_valid(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        cr = Registration.objects.create(
            event=Event.objects.create(
                event_date=timezone.now() + timezone.timedelta(days=4),
                state='open',
                type='class',
            ),
            student=Student.objects.get(pk=3),
            pay_status="refunded",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)
        response = self.client.post(reverse('registration:delete_student', kwargs={'pk': 3}),
                                    {'delete': 'delete', 'pk': 3}, secure=True)
        students = Student.objects.all()
        self.assertEqual(len(students), 5)
        self.assertEqual(len(students.filter(pk=3)), 0)
