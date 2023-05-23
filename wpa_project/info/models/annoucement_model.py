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


class Announcement(models.Model):
    begin_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    announcement = models.TextField()
    status = models.IntegerField(choices=STATUS, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover
        return self.announcement

    def rendered_announcement(self):
        return Template(self.announcement).render(Context({}))
