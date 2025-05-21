from django.urls import path
from .views import *
app_name = 'info'

urlpatterns = [
    path('announcement_form/', AnnouncementFormView.as_view(), name='announcement_form'),
    path('announcement_form/<int:pk>', AnnouncementFormView.as_view(), name='announcement_form'),
    path('announcement_list/', AnnouncementList.as_view(), name='announcement_list'),
    path('category/', CategoryView.as_view(), name='category'),
    path('category/<int:category_id>/', CategoryView.as_view(), name='category'),
    path('category_delete/<int:category_id>/', CategoryDeleteView.as_view(), name='category_delete'),
    path('category_list/', CategoryListView.as_view(), name='category_list'),
    path('faq', FaqList.as_view(), name='faq'),
    path('info/<str:info>/', InfoView.as_view(), name='info'),
    path('edit/', FaqFormView.as_view(), name='edit'),
    path('edit/<int:faq_id>/', FaqFormView.as_view(), name='edit'),
    path('policy/', PolicyFormView.as_view(), name='policy'),
    path('policy/<int:policy>/', PolicyFormView.as_view(), name='policy'),
    path('policy/<int:policy>/<int:version>/', PolicyFormView.as_view(), name='policy'),
    path('policy_list', PolicyListView.as_view(), name='policy_list'),
    path('staff_list/', StaffList.as_view(), name='staff_list'),
    path('staff_profile_form/', StaffProfileFormView.as_view(), name='staff_profile_form'),
    path('staff_profile_form/<int:pk>/', StaffProfileFormView.as_view(), name='staff_profile_form'),
]
