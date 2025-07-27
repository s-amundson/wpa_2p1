from django.urls import path
from .views import *

app_name = 'inventory'
urlpatterns = [
    path('bow_form/', BowFormView.as_view(), name='bow_form'),
    path('bow_form/<int:pk>/', BowFormView.as_view(), name='bow_form'),
    path('bow_list/', BowListView.as_view(), name='bow_list'),
    path('bow_inventory/', BowInventoryView.as_view(), name='bow_inventory'),
    path('bow_inventory/<str:no_camera>/', BowInventoryView.as_view(), name='bow_inventory'),
]
