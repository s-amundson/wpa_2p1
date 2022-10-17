import logging
from django.db import models
from django.utils import timezone
from .category_model import Category
logger = logging.getLogger(__name__)


class Email(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True)
    is_valid = models.BooleanField(default=True)
    ip = models.GenericIPAddressField(default=None, null=True)

