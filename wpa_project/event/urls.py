from django.urls import path
from .views import *
app_name = 'events'
urlpatterns = [
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('cancel/<int:student_family>/', CancelView.as_view(), name='cancel'),
    path('event_attend/<int:registration>/', EventAttendView.as_view(), name='event_attend'),
    path('event_attend_list/<int:event>/', EventAttendListView.as_view(), name='event_attend_list'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('registration/<int:event>/', RegistrationView.as_view(), name='registration'),
    path('volunteer_award/', VolunteerAwardView.as_view(), name='volunteer_award'),
    path('volunteer_award/<int:pk>/', VolunteerAwardView.as_view(), name='volunteer_award'),
    path('volunteer_award_list/', VolunteerAwardListView.as_view(), name='volunteer_award_list'),
    path('volunteer_event/', VolunteerEventView.as_view(), name='volunteer_event'),
    path('volunteer_event/<int:event>/', VolunteerEventView.as_view(), name='volunteer_event'),
    path('volunteer_event_list/', VolunteerEventListView.as_view(), name='volunteer_event_list'),
    path('volunteer_event_list/<int:past>/', VolunteerEventListView.as_view(), name='volunteer_event_list'),
    path('volunteer_record/', VolunteerRecordView.as_view(), name='volunteer_record'),
]
