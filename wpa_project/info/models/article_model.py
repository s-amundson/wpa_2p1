from django.db import models
import logging
logger = logging.getLogger(__name__)

STATUS = (
    (0, "Draft"),
    (1, "Publish"),
    (2, 'Obsolete')
)


class ArticlePage(models.Model):
    page = models.CharField(max_length=40)

    def __str__(self):  # pragma: no cover
        return self.page

class Article(models.Model):
    article = models.TextField()
    page = models.ManyToManyField(ArticlePage)
    position = models.IntegerField(default=0)
    status = models.IntegerField(choices=STATUS, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_html = models.BooleanField(default=False)


    class Meta:
        ordering = ['-created_at']
