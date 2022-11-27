from django import forms
from django.forms import Form

from ..models import User
import logging
logger = logging.getLogger(__name__)


class ThemeForm(Form):
    theme = forms.ChoiceField(choices=User.THEME_CHOICES, widget=forms.RadioSelect())
