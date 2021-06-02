from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User

class UserAdmin(UserAdmin):

    model = User
    list_display = ['email', 'username', 'is_board', 'is_instructor']


admin.site.register(User, UserAdmin)
