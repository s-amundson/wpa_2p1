import logging
from django.db import models
from django.utils import timezone

from student_app.models import Student
from .member_model import Member
from src.model_helper import choices
logger = logging.getLogger(__name__)


class Election(models.Model):
    STATES = ['scheduled', 'open', 'closed']
    election_date = models.DateField(default=timezone.now)
    state = models.CharField(max_length=20, null=True, choices=choices(STATES))
    # description = models.CharField(max_length=150, null=True, default='General Election')

    def __str__(self):
        return f'{self.election_date} {self.state}'

class ElectionPosition(models.Model):
    position = models.CharField(max_length=40)

    def __str__(self):
        return self.position

class ElectionCandidate(models.Model):
    # positions = [(1, 'President'),
    #              (2, 'Vice President'),
    #              (3, 'Secretary'),
    #              (4, 'Treasurer'),
    #              (5, 'Member at Large')]
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    position = models.ForeignKey(ElectionPosition, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.student.first_name} {self.student.last_name}'

class ElectionVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    president = models.ForeignKey(ElectionCandidate, on_delete=models.CASCADE, limit_choices_to={'position': 1},
                                  related_name='president_candidate', null=True)
    vice_president = models.ForeignKey(ElectionCandidate, on_delete=models.CASCADE, limit_choices_to={'position': 2},
                                       related_name='vice_candidate', null=True)
    secretary = models.ForeignKey(ElectionCandidate, on_delete=models.CASCADE, limit_choices_to={'position': 3},
                                  related_name='secretary_candidate', null=True)
    treasurer = models.ForeignKey(ElectionCandidate, on_delete=models.CASCADE, limit_choices_to={'position': 4},
                                  related_name='treasurer_candidate', null=True)
    member_at_large = models.ManyToManyField(ElectionCandidate, limit_choices_to={'position': 5},
                                      related_name='at_large_candidate')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
