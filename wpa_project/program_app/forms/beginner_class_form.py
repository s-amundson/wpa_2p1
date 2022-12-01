from django import forms

from ..models import BeginnerClass

import logging
logger = logging.getLogger(__name__)


class BeginnerClassForm(forms.ModelForm):

    class Meta:
        model = BeginnerClass
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cancel_message'] = forms.CharField(required=False)
        self.fields['event'].required = False
