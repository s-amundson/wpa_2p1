import logging
from django.db import models


logger = logging.getLogger(__name__)


class DiscordChannel(models.Model):
    channel = models.BigIntegerField()
    title = models.CharField(max_length=50)
    level = models.CharField(max_length=20, choices=(
        ('board', 'Board'), ('instructors', 'Instructors'), ('staff', 'Staff'), ('members', 'Members')))

class DiscordChannelRole(models.Model):
    channel=models.ForeignKey(DiscordChannel, on_delete=models.SET_NULL, null=True)
    purpose = models.CharField(max_length=20)

