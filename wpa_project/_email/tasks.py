# Create your tasks here

from celery import shared_task

from django.conf import settings
from django.utils import timezone

from .src import EmailMessage
from .models import BulkEmail, EmailCounts

import logging
logger = logging.getLogger('_email')
from celery.utils.log import get_task_logger
celery_logger = get_task_logger(__name__)


@shared_task
def send_bulk_email():
    celery_logger.warning('send bulk emails')
    be = BulkEmail.objects.filter(sent_time__isnull=True).order_by('-priority', 'created_time')
    logger.warning(be)
    em = EmailMessage()
    for e in be:
        counts = EmailCounts.objects.filter(date=timezone.datetime.today()).last()
        if counts is None or counts.bcc + e.users.count() <= settings.EMAIL_BATCH_DAY_LIMIT:
            em.bcc_from_users(e.users.all())
            em.subject = e.subject
            em.body = e.body
            em.attach_alternative(e.html, 'text/html')
            logger.warning(e.id)
            em.send()
            e.sent_time = timezone.now()
            e.save()
