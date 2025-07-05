from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, DateField, IntegerField, CharField


class User(AbstractUser):
    THEME_CHOICES = [('browser', 'browser'), ('dark', 'dark'), ('light', 'light')]

    is_board = BooleanField(default=False)
    is_instructor = BooleanField(default=False)
    instructor_expire_date = DateField(default=None, null=True)
    dark_theme = BooleanField(default=False)
    is_member = BooleanField(default=False)
    instructor_level = IntegerField(default=None, null=True)
    theme = CharField(max_length=20, choices=THEME_CHOICES, default='browser')

    class Meta:
        permissions = [
            ("board", "For voting board members"),
            ('board_plus', 'For board members and previous President'),
            ('instructors', 'For our active instructors'),
            ('staff', 'for our staff'),
            ('members', 'For members'),
        ]