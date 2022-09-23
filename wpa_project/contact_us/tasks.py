# Create your tasks here
from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.conf import settings
import enchant

from .models import Message, SpamWords
from .src import EmailMessage

import logging
logger = logging.getLogger(__name__)


@shared_task
def send_contact_email(message_id):
    message = Message.objects.get(pk=message_id)
    logging.warning(message.message)
    if message.message.count('.ru') >= 3:
        logging.warning('return .ru')
        return False

    message_array = message.message.split(' ')
    english_words = 0
    other_words = 0
    d = enchant.Dict("en_US")
    for i in range(len(message_array)):
        message_array[i] = message_array[i].lower()
        if d.check(message_array[i]):
            english_words += 1
        else:
            other_words += 1
    if other_words > english_words * 1.5:
        logging.warning('return not english enough')
        return False

    for w in SpamWords.objects.all():
        if message_array.count(w.word):
            logging.warning('return spam words')
            return False
    # send the message
    EmailMessage().contact_email(message)
    message.sent = True
    message.save()
    logging.warning(message.sent)
    return True


