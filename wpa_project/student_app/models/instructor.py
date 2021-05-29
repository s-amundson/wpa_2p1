# import logging
# from django.db import models
# from .student import Student
#
# from django.utils import timezone
# logger = logging.getLogger(__name__)
#
#
# class Instructor(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
#     expire_date = models.DateField()
