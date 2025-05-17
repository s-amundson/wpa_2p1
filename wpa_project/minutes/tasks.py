# Create your tasks here
from celery import shared_task

from .models import Poll

import logging
logger = logging.getLogger('minutes')
from celery.utils.log import get_task_logger
celery_logger = get_task_logger('minutes')


@shared_task
def close_poll(poll_id):
    poll = Poll.objects.get(pk=poll_id)
    poll.state = 'closed'
    poll.save()

