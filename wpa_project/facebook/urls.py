from django.urls import path
from .views import *
app_name = 'facebook'
urlpatterns = [
    path('posts', PostList.as_view(), name='posts'),
    path('posts_include', PostListInsert.as_view(), name='posts_include')
    # path('edit/', FaqFormView.as_view(), name='edit'),
    # path('edit/<int:faq_id>/', FaqFormView.as_view(), name='edit'),
]
