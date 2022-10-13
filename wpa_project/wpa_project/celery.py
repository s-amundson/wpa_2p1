import os

from celery import Celery
from celery.signals import setup_logging
from validate_email import validate_email

import logging
logger = logging.getLogger(__name__)
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wpa_project.settings')

app = Celery('wpa_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from django.conf import settings
    dictConfig(settings.LOGGING)


@app.task(ignore_result=False)
def check_email(address):
    is_valid = validate_email(address, dns_timeout=5, smtp_timeout=5)
    logging.warning(is_valid)
    return is_valid


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
