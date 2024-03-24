from django.urls import path
from .views import *
app_name = 'minutes'
urlpatterns = [
    path('business/<int:business_id>/', BusinessView.as_view(), name='business'),
    path('business/', BusinessView.as_view(), name='business'),
    path('business_update/', BusinessUpdateView.as_view(), name='business_update'),
    path('business_update/<int:update_id>/', BusinessUpdateView.as_view(), name='business_update'),
    path('decision/', DecisionView.as_view(), name='decision'),
    path('decision/<int:decision_id>/', DecisionView.as_view(), name='decision'),
    path('decision_list/', DecisionListView.as_view(), name='decision_list'),
    path('minutes_form/', MinutesFormView.as_view(), name='minutes_form'),
    path('minutes_form/<int:minutes_id>/', MinutesFormView.as_view(), name='minutes_form'),
    path('minutes_list/', MinutesListView.as_view(), name='minutes_list'),
    path('report/', ReportView.as_view(), name='report'),
    path('report/<int:report_id>/', ReportView.as_view(), name='report'),
]