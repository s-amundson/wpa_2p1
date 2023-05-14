from celery import shared_task
import enchant
import requests
from django import forms
from django.conf import settings
from django.utils import timezone
from django_pandas.io import read_frame
# from ipware import get_client_ip
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from .models import BlockedDomain, Email, Message, SpamWords
from .src import EmailMessage

import logging
logger = logging.getLogger(__name__)


@shared_task
def check_spam(message):
    message.is_spam = naive_bayes(message)
    logging.warning(message.is_spam)
    if message.is_spam:
        message.save()
        logging.warning('return naive bayes')
        return False

    # check for spam, since most of the spam seems to be russian we are checking for russian sites and words.
    if message.message.count('.ru') >= 3:
        logging.warning('return .ru')
        return False

    if message.email.strip()[-3:] == '.ru':
        logging.warning('.ru email address')
        return False

    message_array = message.message.split(' ')
    words = {'english': 0, 'spanish': 0, 'russian': 0, 'other': 0}
    en = enchant.Dict("en_US")
    es = enchant.Dict("es")
    ru = enchant.Dict("ru")
    for i in range(len(message_array)):
        message_array[i] = message_array[i].lower()
        is_word = False
        try:
            if en.check(message_array[i]):
                words['english'] += 1
                is_word = True
            if es.check(message_array[i]):
                words['spanish'] += 1
                is_word = True
            if ru.check(message_array[i]):
                words['russian'] += 1
                is_word = True
            if not is_word:
                words['other'] += 1
        except ValueError:
            pass

    if words["russian"] / len(message_array) >= 0.07:
        logging.warning('to many russian words')
        return False

    for w in SpamWords.objects.all():
        if message_array.count(w.word):
            logging.warning('return spam words')
            return False

    return True


def is_it_real(address):  # pragma no cover
    response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params={'email': address},
        headers={'Authorization': "Bearer " + settings.ISITAREALEMAIL_API})
    return response.json()['status']


def naive_bayes(message):
    qs = Message.objects.exclude(spam_category='undetermined')
    if qs:
        df = read_frame(qs, fieldnames=['id', 'message', 'spam_category'], index_col='id')
        df['label'] = df['spam_category'].map({'legit': 0, 'spam': 1})
        cv = CountVectorizer()
        X = cv.fit_transform(df['message'])

        model = MultinomialNB()
        model.fit(X, df['label'])
        data = cv.transform([message.message]).toarray()

        return model.predict(data)[0]
    else:
        return False


@shared_task
def send_contact_email(message_id, client_ip):
    message = Message.objects.get(pk=message_id)
    logging.warning('here')
    naive_bayes(message)
    if message.sent or message.spam_category == 'spam':
        return
    if message.spam_category == 'legit' or check_spam(message):
        try:
            is_valid = validate_email(message.email, client_ip)
        except forms.ValidationError as e:
            is_valid = False
        if is_valid:
            # send the message
            EmailMessage().contact_email(message)
            message.sent = True
            message.save()
            logging.warning(message.sent)


def validate_email(address, client_ip, default_state=True):
    try:
        record = Email.objects.get(email=address)
    except Email.DoesNotExist:
        if client_ip is None or Email.objects.filter(
                ip=client_ip, created_time__gt=timezone.now() - timezone.timedelta(hours=24)).count() > 2:
            logging.warning(f'IP {client_ip} count to high. Address: {address}')
            raise forms.ValidationError("Email validation error")
        u, d = address.split('@')
        logging.warning(f'{u} {d}')
        blocked = BlockedDomain.objects.filter(domain=d).count()
        logging.warning(blocked)
        if blocked:
            raise forms.ValidationError("Email domain blocked")

        # check if we can validate email address.
        count_day = Email.objects.filter(created_time__gt=timezone.now() - timezone.timedelta(hours=24)).count()
        count_hour = Email.objects.filter(created_time__gt=timezone.now() - timezone.timedelta(hours=1)).count()
        logging.warning(f'count hour {count_hour}')

        if count_day > 95 or count_hour > 9:
            logging.warning('Email validation count to high')
            raise forms.ValidationError("Email cannot be checked at this time.")

        record = Email.objects.create(email=address)
        # status = is_it_real(address)
        # # status = 'valid'
        # if status == "valid":
        #     record.is_valid = True
        # elif status == "invalid":
        #     logging.warning(f'{address} is invalid')
        #     record.is_valid = False
        #     raise forms.ValidationError("Email validation error")
        # else:
        #     logging.warning(f'{address} is unknown')
        #     record.is_valid = default_state
        #     if not default_state:
        #         raise forms.ValidationError("Email validation error")
        record.ip = client_ip
        record.save()
    return record.is_valid
