from django.db import models

import logging
logger = logging.getLogger(__name__)


class Posts(models.Model):
    available = models.BooleanField(default=False)
    fetched_time = models.DateTimeField()
    is_live = models.BooleanField(default=False)
    link = models.URLField(null=True)
    post_id = models.PositiveBigIntegerField()
    post_text = models.TextField()
    post_url = models.URLField()
    text = models.TextField()
    time = models.DateTimeField(null=True)
