from django.db import models

import logging
logger = logging.getLogger(__name__)


class Posts(models.Model):
    active = models.BooleanField(default=True)
    post_id = models.CharField(max_length=100, unique=True)
    post_url = models.URLField()
    message = models.TextField()
    created_time = models.DateTimeField(null=True)
