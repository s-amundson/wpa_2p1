from django.urls import path
from .views import *
app_name = 'contact_us'
urlpatterns = [
    path('category/<int:category_id>', CategoryView.as_view(), name='category'),
    path('category', CategoryView.as_view(), name='category'),
    path('category_list', CategoryListView.as_view(), name='category_list'),
    path('contact/', MessageView.as_view(), name='contact'),
]