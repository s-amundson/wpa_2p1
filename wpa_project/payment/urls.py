from django.urls import path
from .views import *
app_name = 'payment'
urlpatterns = [
    path('costs/<int:cost_id>', CostsView.as_view(), name='costs'),
    path('costs', CostsView.as_view(), name='costs'),
    path('process_payment', ProcessPaymentView.as_view(), name='process_payment'),
    path('process_payment/<str:message>/', ProcessPaymentView.as_view(), name='process_payment'),
]