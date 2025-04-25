from django.db import models
from django.template import Context, Template
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

STATUS = (
    (0, "Draft"),
    (1, "Publish"),
    (2, 'Obsolete')
)
ACCESS = (
    ('public', 'Public'),
    ('members', 'Members'),
    ('staff', 'Staff'),
    ('board', 'Board')
)

class Policy(models.Model):
    title = models.CharField(max_length=200)
    access = models.CharField(max_length=40, choices=ACCESS, default='public')

class PolicyText(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    title = models.ForeignKey(Policy, on_delete=models.CASCADE)
    policy = models.TextField()
    is_html = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    # def __str__(self):  # pragma: no cover
    #     return self.policy

    def rendered_policy(self):
        return Template(self.policy).render(Context({}))
