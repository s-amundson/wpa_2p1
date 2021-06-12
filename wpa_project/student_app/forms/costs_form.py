from django import forms
from django.forms import TextInput, ModelForm, DateField, IntegerField, ChoiceField

from ..models import CostsModel


class CostsForm(ModelForm):

    class Meta:
        model = CostsModel
        exclude = []
