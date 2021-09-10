from django import forms
from django.forms import Form

import logging
logger = logging.getLogger(__name__)


class ThemeForm(Form):
    theme = forms.ChoiceField(choices=[('light', 'light'), ('dark', 'dark')], widget=forms.RadioSelect())



