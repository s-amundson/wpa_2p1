# Create your tasks here

from celery import shared_task
from django.db.models import Count

from django.utils import timezone

from celery.utils.log import get_task_logger
import logging
logger = logging.getLogger(__name__)
celery_logger = get_task_logger(__name__)



