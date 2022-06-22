from django.urls import path
from .views import *
app_name = 'payment'
urlpatterns = [
    path('card_remove/', CardRemoveView.as_view(), name='card_remove'),
    path('make_payment/', CreatePaymentView.as_view(), name='make_payment'),
    path('view_payment/<pk>/', PaymentView.as_view(), name='view_payment'),
]
