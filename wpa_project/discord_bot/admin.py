from django.contrib import admin

from .models import DiscordChannel, DiscordChannelRole


@admin.register(DiscordChannel)
class DiscordChannelAdmin(admin.ModelAdmin):
    list_display = ['id', 'channel', 'title', 'level']


@admin.register(DiscordChannelRole)
class DiscordChannelRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'channel', 'purpose']
