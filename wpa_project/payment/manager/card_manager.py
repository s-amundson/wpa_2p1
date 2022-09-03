from django.db import models


class CardManager(models.Manager):
    def get_queryset(self):
        return CardQuerySet(self.model, using=self._db)

    def enabled(self):
        return self.get_queryset().enabled()


class CardQuerySet(models.QuerySet):
    def enabled(self, **kwargs):
        return self.filter(enabled=True)
