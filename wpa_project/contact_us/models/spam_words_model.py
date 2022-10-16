import logging
from django.db import models
from django.conf import settings
from django.utils import timezone
logger = logging.getLogger(__name__)


class SpamWords(models.Model):
    word = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.word}'
