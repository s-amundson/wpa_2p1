import logging
import uuid

from django.apps import apps
from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..src import EmailMessage
from ..models import BeginnerClass, ClassRegistration
from student_app.models import Student

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsClassSendEmail(TestCase):
    fixtures = ['f1', 'f3']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.test_dict = {'message': 'Test message', 'subject': 'Test Subject'}

    def test_get_send_email_bad(self):
        response = self.client.get(reverse('programs:send_email'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_get_send_email_good(self):
        response = self.client.get(reverse('programs:send_email', kwargs={'beginner_class': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/form_as_p.html')

    def test_post_send_email_good(self):
        cr = ClassRegistration(beginner_class=BeginnerClass.objects.get(pk=1),
                               student=Student.objects.get(pk=4),
                               new_student=True,
                               pay_status='paid',
                               idempotency_key=str(uuid.uuid4()))
        cr.save()
        response = self.client.post(reverse('programs:send_email', kwargs={'beginner_class': 1}), self.test_dict,
                                    secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertTrue(mail.outbox[0].body.find('Test message') >= 0)

    def test_off_wait_list_email(self):
        # set up beginner class to have wait list
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 0
        bc.beginner_wait_limit = 0
        bc.returnee_limit = 2
        bc.returnee_wait_limit = 10
        bc.save()

        # add 2 more to the wait list at the same time so they go together.
        user = User.objects.get(pk=3)
        ik = str(uuid.uuid4())
        for i in range(2):
            s = Student.objects.get(pk=i + 5)
            s.safety_class = "2023-06-05"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=False,
                                   pay_status='waiting',
                                   idempotency_key=ik,
                                   user=user)
            cr.save()
        registrations = ClassRegistration.objects.all()
        EmailMessage().wait_list_off(registrations)
        self.assertEqual(len(mail.outbox), 1)
        logging.debug(mail.outbox[0].body)
