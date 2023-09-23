import logging
from django.db import models
logger = logging.getLogger(__name__)


class SpamWords(models.Model):
    word = models.CharField(max_length=50)

    def __str__(self):  # pragma: no cover
        return f'{self.word}'
