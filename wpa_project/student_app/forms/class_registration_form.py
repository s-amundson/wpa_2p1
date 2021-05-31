from django import forms
from django.forms import TextInput, ModelForm

from ..models import ClassRegistration


class ClassRegistrationForm(ModelForm):

    class Meta:
        model = ClassRegistration
        exclude = ['pay_status', 'idempotency_key', 'reg_time']
