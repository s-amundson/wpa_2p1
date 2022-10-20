from allauth.account.forms import SignupForm
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from captcha.fields import ReCaptchaField
from contact_us.tasks import validate_email

import logging
logger = logging.getLogger(__name__)


class SignUpForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.warning("signup")
        terms = reverse_lazy("information:info", kwargs={'info': 'terms'})
        self.fields['terms'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2"}), required=True,
                label=mark_safe(_(f"I have read and agree with the <a href='{terms}'>Terms and Conditions</a>")),
                initial=False)
        self.fields['captcha'] = ReCaptchaField()

    def clean_email(self):
        value = super().clean_email()
        is_valid = validate_email(value)
        if is_valid:
            return value
        logging.warning(f'Invalid email {value}')
        raise forms.ValidationError("Email validation error")
