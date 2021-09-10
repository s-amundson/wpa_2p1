from django.urls import path
from .views import *
app_name = 'programs'
urlpatterns = [
    path('beginner_class/<int:beginner_class>/', BeginnerClassView.as_view(), name='beginner_class'),
    path('beginner_class', BeginnerClassView.as_view(), name='beginner_class'),
    path('class_list', BeginnerClassListView.as_view(), name='class_list'),
    path('class_payment', PaymentView.as_view(), name='class_payment'),
    path('class_registered_table', ClassRegisteredTable.as_view(), name='class_registered_table'),
    path('class_registration/<int:reg_id>', ClassRegistrationView.as_view(), name='class_registration'),
    path('class_registration', ClassRegistrationView.as_view(), name='class_registration'),
    path('class_sign_in/<int:reg_id>', ClassSignInView.as_view(), name='class_sign_in'),
    path('class_status/<str:class_id>/', ClassStatusView.as_view(), name='class_status'),
    path('unregister_class', UnregisterView.as_view(), name='unregister_class'),
]
