from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, DateField


class User(AbstractUser):
    is_board = BooleanField(default=False)
    is_instructor = BooleanField(default=False)
    instructor_expire_date = DateField(default=None, null=True)

    def __str__(self):
        return self.email
