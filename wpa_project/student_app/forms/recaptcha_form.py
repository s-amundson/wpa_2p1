import requests
from django.forms import Form, CharField, URLField, HiddenInput
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


class RecaptchaForm(Form): # pragma: no cover
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['captcha'] = CharField(widget=HiddenInput)
        self.fields['url'] = CharField(widget=HiddenInput)

    def get_score(self, remote_ip):
        data = {"secret": settings.RECAPTCHA_SECRET_KEY_V3, "response": self.cleaned_data['captcha']}
        if remote_ip is not None:
            data['remoteip'] = remote_ip
        try:
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            response_data = response.json()
            if response_data['success']:
                return response_data['score']
            else:
                return None
        except (requests.ConnectionError, requests.RequestException, requests.Timeout, requests.TooManyRedirects):
            return 0

