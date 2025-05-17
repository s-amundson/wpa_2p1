# Create your tasks here
from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.conf import settings
import requests

from .models import Posts

import logging
logger = logging.getLogger('facebook')
from celery.utils.log import get_task_logger
celery_logger = get_task_logger('facebook')

# logger.warning(__name__)


@shared_task
def get_facebook_posts():
    # params = {
    #     'access_token': {settings.FACEBOOK_USER_TOKEN}
    # }
    # response = requests.get(f'https://graph.facebook.com/{settings.FACEBOOK_USER_ID}/accounts', params=params)
    # page_access_token = response.json()['data']['access_token']
    params = {
        'access_token': settings.FACEBOOK_PAGE_TOKEN}
    for i in range(5):
        response = requests.get(f'https://graph.facebook.com/v20.0/{settings.FACEBOOK_PAGE}/feed', params=params)
        response_data = response.json()
        celery_logger.warning(response_data)
        update_posts(response_data)
        params['after'] = response_data['paging']['cursors']['after']


def update_posts(data):
    if 'data' in data:
        page_data = data['data']
        params = {
            'access_token': settings.FACEBOOK_PAGE_TOKEN,
            'fields': 'permalink_url, message'}
        for post in page_data:
            post_response = requests.get(f'https://graph.facebook.com/v20.0/{post["id"]}', params=params)
            prd = post_response.json()
            celery_logger.warning(prd)
            logger.warning(prd)
            Posts.objects.update_or_create(
                post_id=post['id'],
                defaults={'post_id': post['id'],
                          'post_url': prd['permalink_url'],
                          'message': post.get('message', ''),
                          'created_time': post['created_time']},
            )
    return


