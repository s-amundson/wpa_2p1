from django.urls import path
from .views import *
app_name = 'events'
urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('registration/<int:event>/', RegistrationView.as_view(), name='registration'),
    path('volunteer_event/', VolunteerEventView.as_view(), name='volunteer_event'),
    path('volunteer_event/<int:event>/', VolunteerEventView.as_view(), name='volunteer_event'),
    path('volunteer_event_list/', VolunteerEventListView.as_view(), name='volunteer_event_list'),
    path('volunteer_event_list/<int:past>/', VolunteerEventListView.as_view(), name='volunteer_event_list'),
]
