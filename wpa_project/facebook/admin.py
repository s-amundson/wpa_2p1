from django.contrib import admin
from .models import EmbeddedPosts


@admin.register(EmbeddedPosts)
class EmbededAdmin(admin.ModelAdmin):
    list_display = ('id', 'begin_date', 'end_date', 'is_event', 'content')
