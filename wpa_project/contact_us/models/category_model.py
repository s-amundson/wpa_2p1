import logging
from django.db import models
from django.conf import settings
from django.utils import timezone
logger = logging.getLogger(__name__)


class Category(models.Model):
    title = models.CharField(max_length=50)
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, limit_choices_to={'is_staff': True})

    def __str__(self):
        return f'{self.title}'
