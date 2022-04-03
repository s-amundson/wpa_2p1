from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, DateField, IntegerField


class User(AbstractUser):
    is_board = BooleanField(default=False)
    is_instructor = BooleanField(default=False)
    instructor_expire_date = DateField(default=None, null=True)
    dark_theme = BooleanField(default=False)
    is_member = BooleanField(default=False)
    instructor_level = IntegerField(default=None, null=True)
