# Create your tasks here
from celery import shared_task
from facebook_scraper import get_posts
from django.conf import settings
from django.utils import timezone

from .models import Posts

import logging
logger = logging.getLogger(__name__)


@shared_task
def fetch_posts():  # pragma: no cover
    fp = Posts.objects.all()

    for post in get_posts(100024925153290, pages=1, credentials=(settings.FACEBOOK_USER, settings.FACEBOOK_PASSWORD)):
        if not fp.filter(post_id=post['post_id']):
            Posts.objects.create(
                available=post['available'],
                fetched_time=post.get('fetched_time', timezone.now()),
                is_live=post.get('is_live', False),
                link=post['link'],
                post_id=post['post_id'],
                post_text=post['post_text'],
                post_url=post['post_url'],
                text=post['text'],
                time=post.get('time', None)
            )
