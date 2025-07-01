import logging
import base64
import uuid
from django.core import mail
from django.test import TestCase, Client, tag
from django.urls import reverse
from reportlab.pdfgen.canvas import Canvas
from django.core.files.base import File
from django.utils import timezone
from unittest.mock import patch

from _email.models import BulkEmail
from event.models import Event, Registration
from ..models import Student, User
from ..src import EmailMessage
from .helper import remove_signatures

logger = logging.getLogger(__name__)

# @tag('temp')
class TestsEmail(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.send_dict = {'recipients': 'board', 'subject': 'Test Subject', 'message': 'Hi\n Test Message'}

    def tearDown(self):
        # remove any files we made.
        remove_signatures()

    def test_awrl_email(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        sig = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAC2AX4DASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD6pooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD//Z'

        img_format, imgstr = sig.split(';base64,')

        ext = img_format.split('/')[-1]
        with open('img.jpg', 'wb') as f:
            f.write(base64.b64decode(imgstr))

        c = Canvas('mydoc.pdf')
        # f = Frame(inch / 2, inch, 7 * inch, 9 * inch, showBoundary=1)
        c.save()
        student = Student.objects.get(pk=3)
        student.signature = File(open('img.jpg', 'rb'), name=f'3.jpg')
        student.signature_pdf = File(open('mydoc.pdf', 'rb'), name=f'3.pdf')
        student.save()

        em = EmailMessage()
        em.awrl_email(Student.objects.get(pk=3))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers AWRL agreement')
        self.assertTrue(mail.outbox[0].body.find('Attached is the Accident Waiver and Release of Liability') > 0)
        self.assertTrue(len(mail.outbox[0].attachments) > 0)

    def test_bcc_from_students(self):
        em = EmailMessage()
        em.bcc_from_students(Student.objects.all())
        self.assertEqual(len(em.bcc), 5)

    def test_bcc_from_students(self):
        em = EmailMessage()
        em.bcc_from_students(Student.objects.filter(pk=3))
        self.assertEqual(len(em.bcc), 1)
        self.assertEqual(str(em.bcc[0]), "RosalvaAHall@superrito.com")

    def test_get_send_email_auth(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:send_email'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/form_as_p.html')

    def test_get_send_email_no_auth(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:send_email'), secure=True)
        self.assertEqual(response.status_code, 403)

    # @tag('temp')
    @patch('_email.tasks.send_bulk_email.delay')
    def test_send_email_board(self, task_send_email):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('registration:send_email'), self.send_dict, secure=True)
        self.assertRedirects(response, reverse('registration:index'))
        be = BulkEmail.objects.last()
        self.assertEqual(be.subject, self.send_dict['subject'])
        self.assertEqual(be.users.all().count(), 1)
        task_send_email.assert_called()

    # @tag('temp')
    @patch('_email.tasks.send_bulk_email.delay')
    def test_send_email_staff(self, task_send_email):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.send_dict['recipients'] = 'staff'
        response = self.client.post(reverse('registration:send_email'), self.send_dict, secure=True)
        self.assertRedirects(response, reverse('registration:index'))
        be = BulkEmail.objects.last()
        self.assertEqual(be.subject, self.send_dict['subject'])
        self.assertEqual(be.users.all().count(), 2)
        task_send_email.assert_called()

    # @tag('temp')
    @patch('_email.tasks.send_bulk_email.delay')
    def test_send_email_current_members(self, task_send_email):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.send_dict['recipients'] = 'current members'
        response = self.client.post(reverse('registration:send_email'), self.send_dict, secure=True)
        self.assertRedirects(response, reverse('registration:index'))
        be = BulkEmail.objects.last()
        self.assertEqual(be.subject, self.send_dict['subject'])
        self.assertEqual(be.users.all().count(), 1)
        task_send_email.assert_called()

    # @tag('temp')
    @patch('_email.tasks.send_bulk_email.delay')
    def test_send_email_students(self, task_send_email):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        event = Event.objects.create(
            event_date=timezone.now() - timezone.timedelta(days=20),
            type="work",
            cost_standard=0,
            cost_member=0,
            state="open",
            volunteer_points=2
        )
        ik = uuid.uuid4()
        for student in Student.objects.all():
            Registration.objects.create(
                event=event,
                student=student,
                pay_status='paid',
                idempotency_key=ik,
                reg_time="2021-06-09",
                attended=True
            )
        u = User.objects.get(pk=3)
        u.is_active = False
        u.save()

        self.send_dict['recipients'] = 'students'
        response = self.client.post(reverse('registration:send_email'), self.send_dict, secure=True)
        self.assertRedirects(response, reverse('registration:index'))
        be = BulkEmail.objects.last()
        self.assertEqual(be.subject, self.send_dict['subject'])
        self.assertEqual(be.users.all().count(), 5)
        task_send_email.assert_called()

    # @tag('temp')
    @patch('_email.tasks.send_bulk_email.delay')
    def test_send_email_invalid(self, task_send_email):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.send_dict['recipients'] = 'invalid'
        response = self.client.post(reverse('registration:send_email'), self.send_dict, secure=True)
        task_send_email.assert_not_called()
        self.assertEqual(BulkEmail.objects.all().count(), 0)

    # @tag('temp')
    @patch('_email.tasks.send_bulk_email.delay')
    def test_send_email_joad(self, send_bulk_email):
        student = Student.objects.get(pk=3)
        student.is_joad = True
        student.save()

        student = Student.objects.get(pk=4)
        student.is_joad = True
        student.save()

        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.send_dict['recipients'] = 'joad'
        response = self.client.post(reverse('registration:send_email'), self.send_dict, secure=True)
        self.assertRedirects(response, reverse('registration:index'))
        be = BulkEmail.objects.last()
        self.assertEqual(be.subject, self.send_dict['subject'])
        self.assertTrue(be.body.find('Test Message') > 0)
        send_bulk_email.assert_called()
