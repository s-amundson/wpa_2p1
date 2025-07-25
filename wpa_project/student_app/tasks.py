# Create your tasks here

from celery import shared_task

from django.conf import settings
from django.core.files.base import File
from django.utils import timezone

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame, Image, Spacer
from reportlab.lib.pagesizes import letter

from django_celery_beat.models import PeriodicTask

from student_app.src import EmailMessage
from program_app.src import UpdatePrograms
from .models import Student, User

import os
# import logging
# logger = logging.getLogger(__name__)
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@shared_task
def hourly():
    logger.debug('hourly task')
    UpdatePrograms().hourly_update()


@shared_task
def waiver_pdf(student_id, sig_first_name, sig_last_name):
    student = Student.objects.get(pk=student_id)
    if student is None:  # pragma: no cover
        return
    logger.warning(student.signature)
    if not student.signature:
        logger.warning('No Signature')
        return
    sf = student.student_family

    styles = getSampleStyleSheet()
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
    story.append(Paragraph("Student:", styles['Normal']))
    story.append(
        Paragraph(f'&nbsp;&nbsp;&nbsp;&nbsp;{student.first_name} {student.last_name}', styles['Normal']))
    story.append(Paragraph(f'&nbsp;&nbsp;&nbsp;&nbsp;{sf.street}', styles['Normal']))
    story.append(Paragraph(f'&nbsp;&nbsp;&nbsp;&nbsp;{sf.city} {sf.state} {sf.post_code}', styles['Normal']))

    new_sig = Image(student.signature, width=3 * inch, height=1 * inch, hAlign='LEFT')
    story.append(new_sig)
    story.append(Paragraph(f"Signed By {sig_first_name} {sig_last_name} on Date: {student.safety_class}"))
    c = Canvas('mydoc.pdf', pagesize=letter)
    f = Frame(inch / 2, inch / 2, 7 * inch, 10 * inch, showBoundary=1)
    f.addFromList(story, c)
    c.save()
    student.signature_pdf = File(
        open('mydoc.pdf', 'rb'),
        name=f'{student.first_name} {student.last_name}.pdf')
    student.save()
    EmailMessage().awrl_email(student)
    return True
