from django.views.generic import ListView
from ..models import Posts

import logging
logger = logging.getLogger(__name__)


class PostList(ListView):
    paginate_by = 5
    """
    Return all posts that are with available true and order from the latest one.
    """
    template_name = 'facebook/post_list.html'

    def get_queryset(self):
        # logger.warning('facebook get queryset')
        queryset = Posts.objects.filter(active=True).order_by('-created_time')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PostListInsert(PostList):
    template_name = 'facebook/post_list_insert.html'
