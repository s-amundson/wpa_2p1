from django.urls import path
from .views import *
app_name = 'facebook'
urlpatterns = [
    path('add_post', PostAddView.as_view(), name='add_post'),
    path('posts', PostList.as_view(), name='posts'),
    path('posts_include', PostListInsert.as_view(), name='posts_include')
]
