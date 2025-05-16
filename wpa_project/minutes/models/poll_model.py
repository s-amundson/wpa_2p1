import logging
from django.apps import apps
from django.db import models
from django.utils import timezone
from django.conf import settings
from src.model_helper import choices
from ..models import Business, Minutes
logger = logging.getLogger(__name__)

STATES = ['scheduled', 'open', 'closed', 'canceled']

class PollChoices(models.Model):
    choice = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.choice

class PollType(models.Model):
    poll_type = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.poll_type

    @classmethod
    def get_default_pk(self):
        pt, created = self.objects.get_or_create(poll_type='poll')
        return pt.pk


class Poll(models.Model):
    poll_date = models.DateTimeField(default=timezone.now)
    poll_type = models.ForeignKey(PollType, default=PollType.get_default_pk, on_delete=models.PROTECT)
    description = models.CharField(max_length=300)
    level = models.CharField(max_length=20, choices=(
        ('board', 'Board'), ('instructors', 'Instructors'), ('staff', 'Staff'), ('members', 'Members')))
    is_anonymous = models.BooleanField(default=False)
    poll_choices = models.ManyToManyField(PollChoices)
    state = models.CharField(max_length=20, null=True, choices=choices(STATES))
    duration = models.IntegerField(default=1) # hours
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, default=None)
    minutes = models.ForeignKey(Minutes, on_delete=models.SET_NULL, null=True, default=None)

    def get_votes(self):
        return apps.get_model('minutes', 'PollVote').objects.get_vote_count(self)


class PollVoteManager(models.Manager):
    def get_votes(self, poll):
        return self.get_queryset().filter(poll=poll)

    def get_vote_count(self, poll):
        votes = self.get_votes(poll)
        votes = votes.values('choice').annotate(num_votes=models.Count("id"))
        for v in votes:
            v['choice'] = PollChoices.objects.get(pk=v['choice'])
        return votes


class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, default=None, related_name='+')
    choice = models.ForeignKey(PollChoices, on_delete=models.PROTECT, related_name='+')

    objects = PollVoteManager()