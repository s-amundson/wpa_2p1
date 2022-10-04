from celery import shared_task
import enchant
from django_pandas.io import read_frame
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from .models import Message, SpamWords
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

        logging.warning(f'{message_array[i]} english: {words["english"]}, spanish: {words["spanish"]}, russian: {words["russian"]}, other: {words["other"]}')
    if words["russian"] / len(message_array) >= 0.07:
        logging.warning('to many russian words')
        return False

    for w in SpamWords.objects.all():
        if message_array.count(w.word):
            logging.warning('return spam words')
            return False

    return True


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
def send_contact_email(message_id):
    message = Message.objects.get(pk=message_id)
    logging.warning('here')
    naive_bayes(message)
    if message.sent or message.spam_category == 'spam':
        return
    if message.spam_category == 'legit' or check_spam(message):
        # send the message
        EmailMessage().contact_email(message)
        message.sent = True
        message.save()
        logging.warning(message.sent)
