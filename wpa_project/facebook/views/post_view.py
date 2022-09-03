from django.views.generic import ListView

from ..models import Posts

import logging
logger = logging.getLogger(__name__)


class PostList(ListView):
    """
    Return all posts that are with status 1 (published) and order from the latest one.
    """
    queryset = Posts.objects.filter(available=True).order_by('-time')
    template_name = 'facebook/post_list.html'
