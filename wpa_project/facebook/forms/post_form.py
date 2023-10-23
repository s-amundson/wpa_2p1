from django import forms
from django.utils import timezone
from ..models import EmbeddedPosts
import logging

logger = logging.getLogger(__name__)


class PostForm(forms.ModelForm):
    class Meta:
        model = EmbeddedPosts
        fields = ['begin_date', 'end_date', 'is_event', 'content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['begin_date', 'end_date', 'is_event']:
            self.fields[f].required = False
        d = timezone.now()
        self.fields['end_date'].initial = d.replace(year=d.year + 1)
