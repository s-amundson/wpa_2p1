"""
Django settings for wpa_project project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import json
import sys
import os
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

with open(os.path.join(BASE_DIR, 'wpa_project', 'secrets.json')) as secrets_file:
    secret_settings = json.load(secrets_file)


def get_secret(setting, secrets=secret_settings):
    """Get secret setting or fail with ImproperlyConfigured"""
    try:
        return secrets[setting]
    except KeyError:
        raise ImproperlyConfigured("Set the {} setting".format(setting))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_FORMS = {'signup': 'student_app.forms.SignUpForm'}
ALLOWED_HOSTS = get_secret('ALLOWED_HOSTS')
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_RATE_LIMITS = {
    # Change password view (for users already logged in)
    "change_password": "5/m",
    # Email management (e.g. add, remove, change primary)
    "manage_email": "10/m",
    # Request a password reset, global rate limit per IP
    "reset_password": "20/m",
    # Rate limit measured per individual email address
    "reset_password_email": "5/m",
    # Password reset (the view the password reset email links to).
    "reset_password_from_key": "20/m",
    # Signups.
    "signup": "10/h",
    # NOTE: Login is already protected via `ACCOUNT_LOGIN_ATTEMPTS_LIMIT`
}
ACCOUNT_USERNAME_REQUIRED = False



# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'student_app.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # To keep the Browsable API

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_URL = get_secret('CELERY_BROKER')
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_RESULT_PERSISTENT = False
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_IGNORE_RESULT = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",
                   "https://cdnjs.cloudflare.com",
                   "https://*.squareupsandbox.com",
                   "https://*.squareup.com")
CSP_FONT_SRC = ("'self'",
                "https://cdnjs.cloudflare.com",
                "https://*.cloudfront.net", "https://*.squarecdn.com")
CSP_FRAME_ANCESTORS = ("'self'", "https://www.facebook.com", "https://www.google.com")
CSP_FRAME_SRC = ("'self'",
                 "https://*.squarecdn.com",
                 "https://*.squareupsandbox.com",
                 "https://*.squareup.com",
                 "https://www.facebook.com",
                 "https://*.google.com",
                 )
CSP_IMG_SRC = ("'self'", "data:",
               "https://www.facebook.com",
               "http://www.w3.org")
CSP_INCLUDE_NONCE_IN = ['script-src']
CSP_STYLE_SRC = ("'self' 'unsafe-inline'",
                 "https://cdnjs.cloudflare.com",
                 "https://cdn.jsdelivr.net",
                 "https://*.squarecdn.com",
                 "https://*.squareupsandbox.com",
                 "https://*.squareup.com",
                 )
CSP_SCRIPT_SRC = ("'self' 'sha384-7+zCNj/IqJ95wo16oMtfsKbZ9ccEh31eOz1HGyDuCQ6wgnyJNSYdrPa03rtR1zdB' "
                  "'sha384-QJHtvGhmr9XOIpI6YVutG+2QOK9T+ZnN4kzFN1RtK3zEFEIsxhlmWl5/YESvpZ13'",
                  "https://code.jquery.com",
                  "https://cdn.jsdelivr.net",
                  "https://*.squarecdn.com",
                  "https://*.squareupsandbox.com",
                  "https://*.squareup.com",
                  "https://*.facebook.net",
                  "https://*.google.com",
                  "https://*.gstatic.com"
                  )

CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = get_secret("CSRF_TRUSTED_ORIGINS")
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': get_secret("DATABASE"),
}
if 'test' in sys.argv:  # or 'test_coverage' in sys.argv: #Covers regular testing and django-coverage
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_secret("DEBUG")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_FROM_EMAIL = get_secret('DEFAULT_FROM_EMAIL')
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = get_secret("EMAIL_BACKEND") #'django.core.mail.backends.console.EmailBackend'
EMAIL_DEBUG = get_secret("EMAIL_DEBUG")
EMAIL_DEBUG_ADDRESSES = get_secret('EMAIL_DEBUG_ADDRESSES')
EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = get_secret('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD')

FACEBOOK_ID = get_secret('FACEBOOK_ID')
FACEBOOK_PASSWORD = get_secret('FACEBOOK_PASSWORD')
FACEBOOK_USER = get_secret('FACEBOOK_USER')

# Application definition
INSTALLED_APPS = [
    'event',
    'student_app',
    'payment',
    'program_app',
    'membership',
    'minutes',
    'joad',
    'contact_us',
    'info',
    'facebook',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.instagram',

    "sslserver",
    'django_sendfile',
    'django_celery_beat',
    'captcha',
]

ISITAREALEMAIL_API = get_secret('ISITAREALEMAIL_API')
LOGIN_REDIRECT_URL = 'registration:profile'
logger_default = {
        'handlers': ['console'],
        'level': get_secret("DEBUG_LEVEL"),
        'propagate': False,
    }
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'django1': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
        'verbose': {
            'format': 'root: {levelname} {asctime} {pathname}.{funcName} line:{lineno} {message}',
            'style': '{',
        },
        'verbose2': {
            'format': '{levelname} {asctime} {name}.{funcName} line:{lineno} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose2'
        },
        'celery': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose2',
            'level': 'INFO',
        },
        'django console': {
            'class': 'logging.StreamHandler',
            'formatter': 'django1'
        },
        'root_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose2'
        },
    },
    'loggers': {
        '': {'handelers': ['console'], 'level': 'CRITICAL'},
        'event': logger_default,
        'student_app': logger_default,
        'payment': logger_default,
        'program_app': logger_default,
        'membership': logger_default,
        'minutes': logger_default,
        'joad': logger_default,
        'contact_us': logger_default,
        'info': logger_default,
        'facebook': logger_default,
        'django': {
            'handlers': ['django console'],
            'level': get_secret('DJANGO_LOG_LEVEL'),
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['root_console'],
        'level': 'CRITICAL',
    },
}


MEDIA_ROOT = os.path.join(BASE_DIR, 'student_app', 'media')
MEDIA_URL = '/media/'

MIDDLEWARE = [
    'csp.middleware.CSPMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'US'
PRIVATE_LINKS = get_secret('PRIVATE_LINKS')

RECAPTCHA_PRIVATE_KEY = get_secret('RECAPTCHA')['SECRET_KEY']
RECAPTCHA_PUBLIC_KEY = get_secret('RECAPTCHA')['SITE_KEY']
RECAPTCHA_SECRET_KEY_V3 = get_secret('RECAPTCHA')['SECRET_KEY_V3']
RECAPTCHA_SITE_KEY_V3 = get_secret('RECAPTCHA')['SITE_KEY_V3']

SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

ROOT_URLCONF = 'wpa_project.urls'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret('SECRET_KEY')
SECURE_SSL_REDIRECT = False

if DEBUG:
    SENDFILE_BACKEND = 'django_sendfile.backends.development'
else:
    SENDFILE_BACKEND = 'django_sendfile.backends.nginx'
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = MEDIA_URL

SESSION_COOKIE_AGE = get_secret('SESSION_COOKIE_AGE')
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = True
SITE_ID = 1

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email"
        ],
        "AUTH_PARAMS": {
            "access_type": "offline"
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        # 'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        # 'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v7.0',
    }
}

SQUARE_CONFIG = get_secret('SQUARE_CONFIG')
SQUARE_TESTING = False  # to facilitate testing of refunds and such without external requests
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'student_app.context_processors.private_links',
            ],
        },
    },
]

WSGI_APPLICATION = 'wpa_project.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True

