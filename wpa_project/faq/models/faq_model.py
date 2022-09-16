from django.db import models
from django.template import Context, Template
from .category_model import Category
import logging
logger = logging.getLogger(__name__)

STATUS = (
    (0, "Draft"),
    (1, "Publish"),
    (2, 'Obsolete')
)


class Faq(models.Model):
    category = models.ManyToManyField(Category)
    question = models.CharField(max_length=200)
    answer = models.TextField()
    status = models.IntegerField(choices=STATUS, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover
        return self.question

    def rendered_answer(self):
        return Template(self.answer).render(Context({}))
