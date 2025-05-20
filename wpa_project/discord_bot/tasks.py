# Create your tasks here

from celery import shared_task
from django.db.models import Count

from django.utils import timezone
from .send_discord import SendDiscord

from celery.utils.log import get_task_logger
import logging
logger = logging.getLogger(__name__)
celery_logger = get_task_logger('minutes')


@shared_task
def debug_task():
    celery_logger.warning('program debug task')
    SendDiscord(1353451822538293288, 'spend up to $500 test dollars on testing.', True,
                ['Aye', 'Nay', 'Abstain'])

@shared_task(bind=True)
def discord_message(self, message_dict):
    celery_logger.warning(message_dict)
    return {'status': 'success'}
