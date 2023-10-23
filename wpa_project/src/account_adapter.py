from allauth.account.adapter import DefaultAccountAdapter
from django import forms
from django.conf import settings
import logging
logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        logger.warning(email)
        email_domain = email.split('@')[1]
        logger.warning(email_domain)
        if email_domain in settings.ACCOUNT_EMAIL_DOMAIN_BLACKLIST:
            raise forms.ValidationError(f"{email} has been blacklisted")
        return super().clean_email(email)
