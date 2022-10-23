from allauth.account.forms import SignupForm
from django import forms
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from captcha.fields import ReCaptchaField

from contact_us.tasks import validate_email
from contact_us.models import Email

import logging
logger = logging.getLogger(__name__)


class SignUpForm(SignupForm):
    def __init__(self, *args, **kwargs):
        self.client_ip = kwargs.pop('client_ip')
        self.is_routable = kwargs.pop('is_routable')
        super().__init__(*args, **kwargs)
        logging.warning("signup")
        terms = reverse_lazy("information:info", kwargs={'info': 'terms'})
        self.fields['terms'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2"}), required=True,
                label=mark_safe(_(f"I have read and agree with the <a href='{terms}'>Terms and Conditions</a>")),
                initial=False)
        self.fields['captcha'] = ReCaptchaField()


    def clean_email(self):
        address = super().clean_email()
        try:
            record = Email.objects.get(email=address)
            if record.is_valid:
                return address
            else:
                raise forms.ValidationError("Email validation error")
        except Email.DoesNotExist:
            is_valid = validate_email(address, self.client_ip)
            if is_valid:
                return address
            logging.warning(f'Invalid email {address}')
            raise forms.ValidationError("Email validation error")
