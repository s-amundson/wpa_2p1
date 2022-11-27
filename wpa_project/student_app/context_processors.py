from django.conf import settings
from .forms.recaptcha_form import RecaptchaForm


def private_links(request):
    return {
        "BOARD_DOCS": settings.PRIVATE_LINKS['BOARD_DOCS'],
        'RECAPTCHA_SITE_KEY_V2': settings.RECAPTCHA_PUBLIC_KEY,
        "RECAPTCHA_SITE_KEY_V3": settings.RECAPTCHA_SITE_KEY_V3,
        "recaptcha_form": RecaptchaForm(),
    }
