import logging
from django.db import models
from django.utils import timezone
from student_app.models import User
logger = logging.getLogger(__name__)


class Complaint(models.Model):
    category_choices = [('services', 'Services'), ('harassment', 'Harassment'), ('website', 'Website'),
                        ('staff', 'Staff Issues'), ('maintenance', 'Range Maintenance')]

    category = models.CharField(max_length=20, null=True, choices=category_choices)
    created_time = models.DateTimeField(default=timezone.now)
    incident_date = models.DateField(null=True, default=None)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    resolved_date = models.DateTimeField(default=None, null=True)


class ComplaintComment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    comment = models.TextField()
    comment_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
