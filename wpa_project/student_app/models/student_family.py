import logging

from django.contrib.auth.models import User
from django.db import models

from django.utils import timezone
logger = logging.getLogger(__name__)


class StudentFamily(models.Model):
    # user fields
    user = models.ManyToManyField(User)
    street = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=3)
    post_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    # email = models.EmailField(max_length=150)

    # hidden fields
    # email_verified = models.BooleanField(default=False)
    registration_date = models.DateField(default=timezone.now())
    # verification_code = models.CharField(max_length=50, null=True)

