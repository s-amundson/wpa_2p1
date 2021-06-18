from django import forms
from django.forms import TextInput, ModelForm, DateField, IntegerField, ChoiceField

from ..models import BeginnerClass


class BeginnerClassForm(ModelForm):

    class Meta:
        model = BeginnerClass
        exclude = []
