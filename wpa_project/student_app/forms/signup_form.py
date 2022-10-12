from allauth.account.forms import SignupForm
from captcha.fields import CaptchaField
from django import forms
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from validate_email import validate_email

import logging
logger = logging.getLogger(__name__)


class SignUpForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.warning("signup")
        # self.fields['captcha'] = CaptchaField(required=True)
        terms = reverse_lazy("information:info", kwargs={'info': 'terms'})
        self.fields['terms'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2"}), required=True,
                label=mark_safe(_(f"I have read and agree with the <a href='{terms}'>Terms and Conditions</a>")),
                initial=False)

    def clean_email(self):
        value = super().clean_email()
        is_valid = validate_email(value, dns_timeout=5, smtp_timeout=5)
        logging.warning(is_valid)
        if is_valid:
            return value
        logging.warning(f'Invalid email {value}')
        raise forms.ValidationError("Email validation error")
