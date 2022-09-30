from django.views.generic import ListView
from django.conf import settings
from django.utils import timezone
from ..models import EmbeddedPosts

import logging
logger = logging.getLogger(__name__)


class PostList(ListView):
    paginate_by = 5
    """
    Return all posts that are with available true and order from the latest one.
    """
    template_name = 'facebook/post_list.html'

    def get_queryset(self):
        queryset = EmbeddedPosts.objects.filter(
            begin_date__lt=timezone.now(), end_date__gt=timezone.now()).order_by('-begin_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fb_id'] = settings.FACEBOOK_ID
        for ep in EmbeddedPosts.objects.all():
            logging.warning(ep.begin_date)
        return context


class PostListInsert(PostList):
    template_name = 'facebook/post_list_insert.html'
