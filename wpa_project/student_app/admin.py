from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Student, StudentFamily, User


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name']


@admin.register(StudentFamily)
class StudentFamilyAdmin(admin.ModelAdmin):
    list_display = ['id', 'street', 'registration_date']


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = ['id', 'email', 'username', 'is_board', 'is_instructor']

# admin.site.register(User, UserAdmin)
