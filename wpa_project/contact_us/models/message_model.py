import logging
from django.db import models
from django.utils import timezone
from .category_model import Category
logger = logging.getLogger(__name__)


class Message(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    contact_name = models.CharField(max_length=100)
    created_time = models.DateTimeField(default=timezone.now)
    email = models.EmailField()
    message = models.TextField()
    sent = models.BooleanField(default=False)
