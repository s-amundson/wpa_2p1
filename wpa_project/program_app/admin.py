from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BeginnerClass, ClassRegistration


# @admin.register(BeginnerClass)
# class BeginnerClassAdmin(admin.ModelAdmin):
#     list_display = ['id', 'event__class_date', 'event__state']


@admin.register(ClassRegistration)
class ClassRegistrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'beginner_class', 'student', 'pay_status', 'reg_time', 'attended']
