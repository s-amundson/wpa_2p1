from django.urls import path
from .views import *
app_name = 'faq'
urlpatterns = [
    path('', FaqList.as_view(), name='faq'),
    path('category/', CategoryView.as_view(), name='category'),
    path('category/<int:category_id>/', CategoryView.as_view(), name='category'),
    path('category_list/', CategoryListView.as_view(), name='category_list'),
    path('edit/', FaqFormView.as_view(), name='edit'),
    path('edit/<int:faq_id>/', FaqFormView.as_view(), name='edit'),
]
