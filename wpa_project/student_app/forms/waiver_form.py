from django import forms
from django.utils import timezone
from django.conf import settings
from django.core.files.base import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as PIL_Image

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame, Image, Spacer
from reportlab.lib.pagesizes import letter

from student_app.src import EmailMessage, StudentHelper

import io
import os
import base64
import logging

logger = logging.getLogger(__name__)


class WaiverForm(forms.Form):

    def __init__(self, student, *args, **kwargs):
        self.student = student
        of_age = False
        age_date = kwargs.get('age_date', timezone.now().date())
        initial = kwargs.get('initial', {})
        if 'initial' in kwargs:
            kwargs.pop('initial')
        if student is not None:
            of_age = StudentHelper().calculate_age(student.dob, age_date) >= 18
            initial['signature'] = student.signature
            if of_age:
                initial['sig_first_name'] = student.first_name
                initial['sig_last_name'] = student.last_name
        for k in ['age_date']:
            if k in kwargs:  # pragma: no cover
                kwargs.pop(k)
        super().__init__(initial=initial, *args, **kwargs)

        self.fields['signature'] = forms.CharField(widget=forms.HiddenInput())

        for f in ['sig_last_name', 'sig_first_name']:
            self.fields[f] = forms.CharField()
            if of_age:
                self.fields[f].required = False
                self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'readonly': 'readonly'})
            else:
                self.fields[f].widget.attrs.update({'class': 'form-control m-2'})

    def check_signature(self, class_date=timezone.localtime(timezone.now()).date()):
        sig = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAC2AX4DASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD6pooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD//Z'
        if self.cleaned_data['signature'] == sig:
            logging.error('invalid signature')
            self.add_error(None, 'invalid signature')
            return False

        img = self.decodeImage()
        if img is None:
            logging.debug('img is None')
            return False
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        self.student.signature = InMemoryUploadedFile(
            img_io,
            field_name=None,
            name=f'{self.student.last_name}_{self.student.first_name}.jpg',
            content_type='image/jpeg',
            size=img_io.tell,
            charset=None)
        self.student.safety_class = class_date
        self.student.save()

        return True

    def decodeImage(self):
        image_b64 = self.cleaned_data['signature']
        img_format, imgstr = image_b64.split(';base64,')
        try:
            data = base64.b64decode(imgstr)
            buf = io.BytesIO(data)
            img = PIL_Image.open(buf)
            return img
        except:
            return None

    # def make_pdf(self, class_date=timezone.localtime(timezone.now()).date()):
    #     sf = self.student.student_family
    #
    #     styles = getSampleStyleSheet()
    #     path = os.path.join(settings.BASE_DIR, 'student_app', 'static', 'images', 'WPAHeader4.jpg')
    #     story = [Image(path, width=5 * inch, height=5 * inch / 8), Spacer(1, 0.2 * inch)]
    #
    #     with open(os.path.join(settings.BASE_DIR, 'program_app', 'templates', 'program_app', 'awrl.txt'), 'r') as f:
    #         story.append(Paragraph(f.readline(), styles['Normal']))
    #         story.append(Spacer(1, 0.2 * inch))
    #         story.append(Paragraph(f.readline(), styles['Normal']))
    #         story.append(Spacer(1, 0.1 * inch))
    #         for line in f.readlines():
    #             story.append(Paragraph(line, styles['Bullet']))
    #             story.append(Spacer(1, 0.1 * inch))
    #     story.append(Paragraph("Student:", styles['Normal']))
    #     story.append(
    #         Paragraph(f'&nbsp;&nbsp;&nbsp;&nbsp;{self.student.first_name} {self.student.last_name}', styles['Normal']))
    #     story.append(Paragraph(f'&nbsp;&nbsp;&nbsp;&nbsp;{sf.street}', styles['Normal']))
    #     story.append(Paragraph(f'&nbsp;&nbsp;&nbsp;&nbsp;{sf.city} {sf.state} {sf.post_code}', styles['Normal']))
    #
    #     new_sig = Image('img.jpg', width=3 * inch, height=1 * inch, hAlign='LEFT')
    #     story.append(new_sig)
    #     name = f"{self.cleaned_data['sig_first_name']} {self.cleaned_data['sig_last_name']}"
    #     story.append(Paragraph(f"Signed By {name} on Date: {timezone.localtime(timezone.now()).date()}"))
    #     c = Canvas('mydoc.pdf', pagesize=letter)
    #     f = Frame(inch / 2, inch / 2, 7 * inch, 10 * inch, showBoundary=1)
    #     f.addFromList(story, c)
    #     c.save()
    #     fn = f'{self.student.last_name}_{self.student.first_name}'
    #     self.student.signature = File(open('img.jpg', 'rb'), name=f'{fn}.jpg')
    #     self.student.signature_pdf = File(open('mydoc.pdf', 'rb'), name=f'{fn}.pdf')
    #     self.student.safety_class = class_date
    #     self.student.save()
    #     return True

    def send_pdf(self):
        # send email to user with the waiver attached
        EmailMessage().awrl_email(self.student)
