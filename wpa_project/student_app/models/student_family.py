import logging

from django.conf import settings
from django.db import models

from django.utils import timezone
from ..fields import PhoneField
logger = logging.getLogger(__name__)


class StudentFamily(models.Model):
    # user fields
    street = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=3)
    post_code = models.CharField(max_length=10)
    phone = PhoneField(max_length=20)

    # hidden fields
    registration_date = models.DateField(default=timezone.now)


