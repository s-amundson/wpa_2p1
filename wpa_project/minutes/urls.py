from django.urls import path
from .views import *

app_name = 'minutes'
urlpatterns = [
    path('business/<int:minutes>/<int:business_id>/', BusinessView.as_view(), name='business'),
    path('business/<int:minutes>/', BusinessView.as_view(), name='business'),
    path('decision/', DecisionView.as_view(), name='decision'),
    path('decision/<int:decision_id>/', DecisionView.as_view(), name='decision'),
    path('decision_list/', DecisionListView.as_view(), name='decision_list'),
    path('minutes/', MinutesView.as_view(), name='minutes'),
    path('minutes/<int:minutes>/', MinutesView.as_view(), name='minutes'),
    path('minutes_list/', MinutesListView.as_view(), name='minutes_list'),
    path('motion/', PollView.as_view(), kwargs={'poll_type': 'motion'}, name='motion'),
    path('motion_list/', PollListView.as_view(), kwargs={'poll_type': 'motion'}, name='motion_list'),
    path('poll/', PollView.as_view(), name='poll'),
    path('poll/<int:pk>/', PollView.as_view(), name='poll'),
    # path('poll_detail/<int:pk>/', PollDetailView.as_view(), name='poll_detail'),
    path('poll_list/', PollListView.as_view(), name='poll_list'),
    path('poll_vote/<int:poll>/', PollVoteView.as_view(), name='poll_vote'),
    path('report/', ReportView.as_view(), name='report'),
    path('report/<int:report_id>/', ReportView.as_view(), name='report'),
]