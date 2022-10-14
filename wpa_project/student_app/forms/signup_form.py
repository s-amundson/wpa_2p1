import time
from allauth.account.forms import SignupForm
from django import forms
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.utils import timezone

from contact_us.models import Email
from contact_us.tasks import validate_email

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
        # u, d = value.split('@')
        # logging.warning(f'{u} {d}')
        # with open('block_domains.txt', 'r') as f:
        #     blocked = f.readlines()
        # logging.warning(blocked)
        # if d in blocked:
        #     logging.warning(d)
        #     raise forms.ValidationError("Email domain blocked")
        #
        # # check if we can validate email address.
        # count = Email.objects.filter(created_time__gt=timezone.now() + timezone.timedelta(hours=24)).count()
        # if count > 95:
        #     raise forms.ValidationError("Email cannot be checked at this time.")
        is_valid = validate_email(value)
        if is_valid:
            return value
        logging.warning(f'Invalid email {value}')
        raise forms.ValidationError("Email validation error")
