import logging

from django.test import TestCase, tag, override_settings
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from django.template.loader import get_template

from student_app.models import Student, User
from ..models import BulkEmail, EmailCounts
from ..src import EmailMessage
from ..tasks import send_bulk_email
logger = logging.getLogger(__name__)


@override_settings(EMAIL_BCC_LIMIT=5)
class TestsSend(TestCase):
    fixtures = ['fixture_email1']
    em = EmailMessage()

    # @tag('temp')
    def test_send_to(self):
        self.em.get_email_address(User.objects.get(pk=2))
        logger.warning(self.em.to)

        d = {'name': 'test user', 'paragraphs': []}
        self.em.subject = 'Test Subject'
        self.em.body = get_template('email/paragraph_message.txt').render(d)
        self.em.attach_alternative(get_template('email/paragraph_message.html').render(d), 'text/html')
        self.em.send()

        counts = EmailCounts.objects.last()
        logger.warning(len(EmailCounts.objects.all()))
        self.assertEqual(counts.to, 1)
        self.assertEqual(counts.cc, 0)
        self.assertEqual(counts.bcc, 0)

    # @tag('temp')
    def test_send_cc(self):
        self.em.cc = ['RosalvaAHall@superrito.com']

        d = {'name': 'test user', 'paragraphs': []}
        self.em.subject = 'Test Subject'
        self.em.body = get_template('email/paragraph_message.txt').render(d)
        self.em.attach_alternative(get_template('email/paragraph_message.html').render(d), 'text/html')
        self.em.send()

        counts = EmailCounts.objects.last()
        logger.warning(len(EmailCounts.objects.all()))
        self.assertEqual(counts.to, 0)
        self.assertEqual(counts.cc, 1)
        self.assertEqual(counts.bcc, 0)

    # @tag('temp')
    def test_send_bcc(self):
        self.em.bcc = ['RosalvaAHall@superrito.com']

        d = {'name': 'test user', 'paragraphs': []}
        self.em.subject = 'Test Subject'
        self.em.body = get_template('email/paragraph_message.txt').render(d)
        self.em.attach_alternative(get_template('email/paragraph_message.html').render(d), 'text/html')
        self.em.send()

        counts = EmailCounts.objects.last()
        self.assertEqual(counts.to, 0)
        self.assertEqual(counts.cc, 0)
        self.assertEqual(counts.bcc, 1)

    # @tag('temp')
    def test_send_bulk_bcc(self):
        d = {'name': 'test user', 'paragraphs': []}
        users = User.objects.filter(id__lte=12)
        logger.warning(users)
        self.em.send_mass_bcc(users,
                              'Test Subject',
                              get_template('email/paragraph_message.txt').render(d),
                              get_template('email/paragraph_message.html').render(d))

        bulk_emails = BulkEmail.objects.all()
        self.assertEqual(bulk_emails.count(), 3)
        self.assertEqual(bulk_emails[0].users.count(), 5)
        self.assertEqual(bulk_emails[1].users.count(), 5)
        self.assertEqual(bulk_emails[2].users.count(), 2)

    # @tag('temp')
    @override_settings(EMAIL_BATCH_DAY_LIMIT=10)
    def test_send_bulk_task(self):
        users = User.objects.filter(id__lte=12)
        logger.warning(users)
        for i in range(0, len(users), 5):
            if len(users) - i > 5:
                bcc = users[i: i + 5]
            else:
                bcc = users[i:]
            logger.warning(bcc)
            bulk_email = BulkEmail.objects.create(subject='Test Subject', body='test body', html='test html')
            bulk_email.users.add(*bcc)
        send_bulk_email()
        bulk_emails = BulkEmail.objects.all()
        self.assertEqual(bulk_emails.count(), 3)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        counts = EmailCounts.objects.filter(date=timezone.datetime.today()).last()
        self.assertEqual(counts.bcc, 10)

    # @tag('temp')
    @override_settings(EMAIL_BATCH_DAY_LIMIT=10)
    def test_send_bulk_task_priority(self):
        users = User.objects.filter(id__lte=12)
        logger.warning(users)
        for i in range(0, len(users), 5):
            if len(users) - i > 5:
                bcc = users[i: i + 5]
            else:
                bcc = users[i:]
            logger.warning(bcc)
            bulk_email = BulkEmail.objects.create(subject='Test Subject', body='test body', html='test html')
            bulk_email.users.add(*bcc)
        bulk_email.priority = 1
        bulk_email.save()
        logger.warning(bulk_email.id)
        send_bulk_email()
        bulk_emails = BulkEmail.objects.all()
        self.assertEqual(bulk_emails.count(), 3)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        counts = EmailCounts.objects.filter(date=timezone.datetime.today()).last()
        self.assertEqual(counts.bcc, 7)
