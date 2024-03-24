from django.db import models
from django.utils import timezone

from student_app.models import Student

import logging
logger = logging.getLogger(__name__)


def attachment_name(instance, filename):
    return '/'.join(['reimbursement', str(instance.reimbursement.id), filename])


class ReimbursementVoteManager(models.Manager):

    def get_votes(self, reimbursement):
        return self.get_queryset().filter(reimbursement=reimbursement, timestamp__gt=reimbursement.modified)

    def get_vote_count(self, reimbursement):
        votes = self.get_votes(reimbursement)
        votes = votes.aggregate(yes=models.Count('id', filter=models.Q(approve=True)),
                                no=models.Count('id', filter=models.Q(approve=False)))
        return votes


class Reimbursement(models.Model):
    STATUS_CHOICES = [('pending', 'pending'), ('approved', 'approved'), ('paid', 'paid'), ('denied', 'denied')]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    note = models.TextField(null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(default=timezone.now)


class ReimbursementItem(models.Model):
    reimbursement = models.ForeignKey(Reimbursement, on_delete=models.CASCADE)
    amount = models.FloatField()
    description = models.CharField(max_length=100)
    attachment = models.FileField(upload_to=attachment_name)


class ReimbursementVote(models.Model):
    reimbursement = models.ForeignKey(Reimbursement, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    approve = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ReimbursementVoteManager()
