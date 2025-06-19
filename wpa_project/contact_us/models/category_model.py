import logging
from django.db import models
from django.conf import settings
from django.utils import timezone
logger = logging.getLogger(__name__)


class Category(models.Model):
    title = models.CharField(max_length=50)
    email = models.EmailField(null=True, default=None)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.title}'
