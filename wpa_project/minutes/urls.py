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
    path('report/', ReportView.as_view(), name='report'),
    path('report/<int:report_id>/', ReportView.as_view(), name='report'),
]