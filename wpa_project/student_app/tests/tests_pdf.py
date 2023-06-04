import logging
import base64
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps
from reportlab.pdfgen.canvas import Canvas
from django.core.files.base import File
from ..models import Student
from .helper import remove_signatures
logger = logging.getLogger(__name__)


class TestsPdf(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        sig = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAC2AX4DASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD6pooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD//Z'

        img_format, imgstr = sig.split(';base64,')

        ext = img_format.split('/')[-1]
        with open('img.jpg', 'wb') as f:
            f.write(base64.b64decode(imgstr))

        c = Canvas('mydoc.pdf')
        # f = Frame(inch / 2, inch, 7 * inch, 9 * inch, showBoundary=1)
        c.save()

    def tearDown(self):
        # remove any files we made.
        remove_signatures()

    def test_get_pdf_auth(self):
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)

        student = Student.objects.get(pk=3)
        student.signature = File(open('img.jpg', 'rb'), name=f'3.jpg')
        student.signature_pdf = File(open('mydoc.pdf', 'rb'), name=f'3.pdf')
        student.save()
        response = self.client.get(reverse('registration:pdf', kwargs={'student_id': 3}), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_get_pdf_auth_board(self):
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        student = Student.objects.get(pk=3)
        student.signature = File(open('img.jpg', 'rb'), name=f'3.jpg')
        student.signature_pdf = File(open('mydoc.pdf', 'rb'), name=f'3.pdf')
        student.save()
        response = self.client.get(reverse('registration:pdf', kwargs={'student_id': 3}), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_get_pdf_no_auth(self):
        self.test_user = self.User.objects.get(pk=4)
        self.client.force_login(self.test_user)

        student = Student.objects.get(pk=3)
        student.signature = File(open('img.jpg', 'rb'), name=f'3.jpg')
        student.signature_pdf = File(open('mydoc.pdf', 'rb'), name=f'3.pdf')
        student.save()
        response = self.client.get(reverse('registration:pdf', kwargs={'student_id': 3}), secure=True)
        self.assertEqual(response.status_code, 404)

    def test_get_pdf_no_pdf(self):
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('registration:pdf', kwargs={'student_id': 3}), secure=True)
        self.assertEqual(response.status_code, 403)
