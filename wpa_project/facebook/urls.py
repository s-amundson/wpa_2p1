from django.urls import path
from .views import *
app_name = 'facebook'
urlpatterns = [
    path('page_update_hook', PageHook.as_view(), name='page_update_hook'),
    path('posts', PostList.as_view(), name='posts'),
    path('posts_include', PostListInsert.as_view(), name='posts_include'),
]
