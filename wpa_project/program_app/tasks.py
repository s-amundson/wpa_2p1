# Create your tasks here
from celery import shared_task

from .src import ClassRegistrationHelper
from .models import BeginnerClass, ClassRegistration

import logging
logger = logging.getLogger(__name__)
crh = ClassRegistrationHelper()


@shared_task
def charge_group(reg_list):
    crh.charge_group(ClassRegistration.objects.filter(id__in=reg_list))


@shared_task
def update_waiting(beginner_class):
    crh.update_waiting(beginner_class)
