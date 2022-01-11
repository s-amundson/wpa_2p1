import logging
import base64
import os
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.core.files.base import File
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from ..forms import ClassSignInForm
from ..models import ClassRegistration
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame, Image, Spacer
from ..src.class_registration_helper import ClassRegistrationHelper
from student_app.src.email import EmailMessage

logger = logging.getLogger(__name__)


class ClassSignInView(LoginRequiredMixin, View):
    def get(self, request, reg_id):
        cr = get_object_or_404(ClassRegistration, pk=reg_id)
        of_age = ClassRegistrationHelper().calc_age(cr.student, cr.beginner_class.class_date) > 18
        logging.debug(of_age)
        sig_first_name = ''
        sig_last_name = ''
        if of_age:
            sig_first_name = cr.student.first_name
            sig_last_name = cr.student.last_name
        form = ClassSignInForm(initial={'signature': cr.student.signature, 'sig_first_name': sig_first_name,
                                        'sig_last_name': sig_last_name}, of_age=of_age)
        logging.debug(bool(cr.student.signature))
        logging.debug(cr.student.signature is not None)
        return render(request, 'program_app/class_sign_in.html',
                      {'form': form, 'student': cr.student, 'Img': cr.student.signature,
                       'is_signed': bool(cr.student.signature)})

    def post(self, request, reg_id):
        logging.debug(request.POST)
        cr = get_object_or_404(ClassRegistration, pk=reg_id)
        form = ClassSignInForm(request.POST)
        if form.is_valid():
            logging.debug('valid')
            logging.debug(form.cleaned_data)
            sig = {'signature': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAC2AX4DASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD6pooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD//Z'}
            if form.cleaned_data['signature'] == sig:
                logging.error('invalid signature')
            image_b64 = form.cleaned_data['signature']

            img_format, imgstr = image_b64.split(';base64,')

            ext = img_format.split('/')[-1]
            with open('img.jpg', 'wb') as f:
                f.write(base64.b64decode(imgstr))

            styles = getSampleStyleSheet()
            # styleN = styles['Normal']
            # styleH = styles['Heading4']
            path = os.path.join(settings.BASE_DIR, 'student_app', 'static', 'images', 'WPAHeader4.jpg')
            story = [Image(path, width=5 * inch, height=5 * inch / 8), Spacer(1, 0.2 * inch)]

            with open(os.path.join(settings.BASE_DIR, 'program_app', 'templates', 'program_app', 'awrl.txt'), 'r') as f:
                story.append(Paragraph(f.readline(), styles['Normal']))
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph(f.readline(), styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
                for line in f.readlines():
                    story.append(Paragraph(line, styles['Bullet']))
                    story.append(Spacer(1, 0.1 * inch))

            new_sig = Image('img.jpg', width=3 * inch, height=1 * inch)
            story.append(new_sig)
            d = cr.beginner_class.class_date
            name = f"{form.cleaned_data['sig_first_name']} {form.cleaned_data['sig_last_name']}"
            story.append(Paragraph(f"Signed on Date: {d.date()} By {name}"))
            c = Canvas('mydoc.pdf')
            f = Frame(inch / 2, inch, 7 * inch, 9 * inch, showBoundary=1)
            f.addFromList(story, c)
            c.save()
            cr.student.signature = File(open('img.jpg', 'rb'), name=f'{reg_id}.jpg')
            cr.student.signature_pdf = File(open('mydoc.pdf', 'rb'), name=f'{reg_id}.pdf')
            cr.student.save()
            cr.attended = True
            cr.save()

            # send email to user with the waiver attached
            EmailMessage().awrl_email(cr.student)

            return HttpResponseRedirect(reverse('programs:beginner_class',
                                                kwargs={'beginner_class': cr.beginner_class.id}))
        else:
            logging.debug(form.errors)
            return render(request, 'program_app/class_sign_in.html',
                          {'form': form, 'student': cr.student, 'Img': cr.student.signature,
                           'is_signed': bool(cr.student.signature), 'message': 'invalid signature'})
