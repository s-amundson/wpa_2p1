from django.db import models
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)


class EmbeddedPosts(models.Model):
    begin_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=None, null=True)
    is_event = models.BooleanField(default=False)
    content = models.TextField()