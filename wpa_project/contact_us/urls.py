from django.urls import path
from .views import *
app_name = 'contact_us'
urlpatterns = [
    path('category/<int:category_id>/', CategoryView.as_view(), name='category'),
    path('category/', CategoryView.as_view(), name='category'),
    path('category_list/', CategoryListView.as_view(), name='category_list'),
    path('complaint/', ComplaintView.as_view(), name='complaint'),
    path('complaint/<int:pk>/', ComplaintView.as_view(), name='complaint'),
    path('complaint_list/', ComplaintListView.as_view(), name='complaint_list'),
    path('contact/', MessageView.as_view(), name='contact'),
    path('contact/<int:message_id>/', MessageView.as_view(), name='contact'),
    path('delete_category/<int:category_id>/', CategoryDeleteView.as_view(), name='delete_category'),
    path('message_list/', MessageListView.as_view(), name='message_list'),
    path('message_list/<int:spam>/', MessageListView.as_view(), name='message_list'),
    path('thanks', ThanksView.as_view(), name='thanks')
]
