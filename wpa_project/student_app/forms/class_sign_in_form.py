from datetime import timedelta
from django import forms

import logging

logger = logging.getLogger(__name__)


class ClassSignInForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['signature'] = forms.CharField(widget=forms.HiddenInput())


