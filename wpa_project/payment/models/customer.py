from django.conf import settings
from django.db import models

import logging
logger = logging.getLogger(__name__)


class Customer(models.Model):
    customer_id = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(null=True, default=None)
    creation_source = models.CharField(max_length=50, null=True)
    updated_at = models.DateTimeField(null=True, default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    version = models.IntegerField(default=0)
