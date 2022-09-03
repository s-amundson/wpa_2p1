from django.urls import path
from .views import PostList
app_name = 'facebook'
urlpatterns = [
    path('posts', PostList.as_view(), name='posts'),
    # path('edit/', FaqFormView.as_view(), name='edit'),
    # path('edit/<int:faq_id>/', FaqFormView.as_view(), name='edit'),
]
