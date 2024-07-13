import logging
from django.db import models
from django.utils import timezone
from django.conf import settings
logger = logging.getLogger(__name__)


class BulkEmail(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    sent_time = models.DateTimeField(default=None, null=True)
    priority = models.IntegerField(default=0)
    subject = models.CharField(max_length=100)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    body = models.TextField()
    html = models.TextField(default=None, null=True)


class EmailCounts(models.Model):
    date = models.DateField(default=timezone.datetime.today, unique_for_date=True)
    to = models.IntegerField(default=0)
    cc = models.IntegerField(default=0)
    bcc = models.IntegerField(default=0)
