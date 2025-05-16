from django.contrib import admin
from .models import Poll, PollChoices, PollVote, PollType

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['id', 'poll_date', 'poll_type', 'description', 'level', 'state']

@admin.register(PollChoices)
class PollChoices(admin.ModelAdmin):
    list_display = ['id', 'choice', ]

@admin.register(PollType)
class PollAdmin(admin.ModelAdmin):
    list_display = ['id', 'poll_type']