import logging

from django.test import TestCase, Client
from django.apps import apps

from allauth.account.models import EmailAddress
from allauth.account import signals

from student_app.models import Student
logger = logging.getLogger(__name__)


class TestsSignal(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_email_update_signal(self):
        user = self.User.objects.get(pk=1)
        email = EmailAddress.objects.create(
            user=user, email="john@example.org", primary=False, verified=True
        )

        signals.email_changed.send(
            sender=user.__class__,
            request=None,
            user=user,
            from_email_address=EmailAddress.objects.get_primary(user),
            to_email_address=email,
        )

        s = Student.objects.get(pk=1)
        self.assertEqual(s.email, 'john@example.org')

    def test_email_confirmed_signal(self):
        student = Student.objects.get(pk=3)
        student.email = "john@example.org"
        student.save()
        user = self.User.objects.create(username="john", email="john@example.org")
        logging.debug(user)
        email = EmailAddress.objects.create(
            user=user, email="john@example.org", primary=False, verified=True
        )

        signals.email_confirmed.send(
            sender=None,
            request=None,
            email_address=email,
        )

        s = Student.objects.get(pk=3)
        self.assertEqual(s.email, 'john@example.org')
        self.assertEqual(s.user, user)
