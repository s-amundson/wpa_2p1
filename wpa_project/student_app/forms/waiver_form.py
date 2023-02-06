from django import forms
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as PIL_Image


from student_app.src import EmailMessage, StudentHelper

import io
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
        if img is None:  # pragma: no cover
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
        if self.student.safety_class is None:
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
        except:  # pragma: no cover
            return None

    def send_pdf(self):
        # send email to user with the waiver attached
        EmailMessage().awrl_email(self.student)
