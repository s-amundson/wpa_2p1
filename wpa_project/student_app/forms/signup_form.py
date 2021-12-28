from allauth.account.forms import SignupForm
from django import forms
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


class SignUpForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        terms = reverse_lazy("registration:terms")
        self.fields['terms'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2"}), required=True,
                label=mark_safe(_(f"I have read and agree with the <a href='{terms}'>Terms and Conditions</a>")),
                initial=False)
