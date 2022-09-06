from django.views.generic import ListView
from django.conf import settings

from ..models import Posts

import logging
logger = logging.getLogger(__name__)


class PostList(ListView):
    paginate_by = 5
    """
    Return all posts that are with available true and order from the latest one.
    """
    queryset = Posts.objects.filter(available=True).order_by('-time')
    template_name = 'facebook/post_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fb_id'] = settings.FACEBOOK_ID
        logging.warning(context['object_list'])
        return context


class PostListInsert(PostList):
    template_name = 'facebook/post_list_insert.html'
