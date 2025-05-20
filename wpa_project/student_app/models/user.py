from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, DateField, IntegerField, CharField, BigIntegerField


class User(AbstractUser):
    THEME_CHOICES = [('browser', 'browser'), ('dark', 'dark'), ('light', 'light')]

    is_board = BooleanField(default=False)
    is_instructor = BooleanField(default=False)
    instructor_expire_date = DateField(default=None, null=True)
    dark_theme = BooleanField(default=False)
    is_member = BooleanField(default=False)
    instructor_level = IntegerField(default=None, null=True)
    theme = CharField(max_length=20, choices=THEME_CHOICES, default='browser')
    discord_user = BigIntegerField(null=True, default=None)
