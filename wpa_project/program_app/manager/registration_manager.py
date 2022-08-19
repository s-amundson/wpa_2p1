from django.db import models
from django.utils import timezone


class RegistrationManager(models.Manager):
    def get_queryset(self):
        return RegistrationQuerySet(self.model, using=self._db)

    def attendance(self):
        return self.get_queryset().attendance()


                                                      #

class RegistrationQuerySet(models.QuerySet):
    def attendance(self):
        return self.filter(
            beginner_class__class_date__lt=timezone.now().today(),
            pay_status__in=['paid', 'admin']
        ).aggregate(
            attended=models.Count('id', filter=models.Q(attended=True)),
            registrations=models.Count('id', distinct=True)
        )

    def attended_count(self):
        return self.attendance()['attended']
