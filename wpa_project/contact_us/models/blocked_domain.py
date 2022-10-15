import logging
from django.db import models
from django.utils import timezone
from .category_model import Category
logger = logging.getLogger(__name__)


class BlockedDomain(models.Model):
    domain = models.CharField(max_length=50, unique=True)


