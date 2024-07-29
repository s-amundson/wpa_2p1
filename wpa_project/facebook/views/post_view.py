from django.views.generic import ListView
from django.conf import settings
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from src.mixin import BoardMixin
from ..forms import PostForm
from ..models import EmbeddedPosts, Posts
from ..tasks import get_facebook_posts
import requests

import logging
logger = logging.getLogger(__name__)


class PostAddView(BoardMixin, CreateView):
    model = EmbeddedPosts
    form_class = PostForm
    template_name = 'student_app/form_as_p.html'
    success_url = reverse_lazy('facebook:posts')


class PostList(ListView):
    paginate_by = 5
    """
    Return all posts that are with available true and order from the latest one.
    """
    template_name = 'facebook/post_list.html'

    def get_queryset(self):
        queryset = Posts.objects.filter(active=True).order_by('-created_time')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PostListInsert(PostList):
    template_name = 'facebook/post_list_insert.html'
