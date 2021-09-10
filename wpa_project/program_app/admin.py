from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BeginnerClass


@admin.register(BeginnerClass)
class BeginnerClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'class_date', 'state']
