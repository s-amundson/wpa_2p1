from django.urls import path
from .views import *
app_name = 'membership'
urlpatterns = [
    path('level/<int:level_id>', LevelView.as_view(), name='level'),
    path('level', LevelView.as_view(), name='level'),
    path('level_api', LevelApiView.as_view(), name='level_api'),
    path('membership', MembershipView.as_view(), name='membership'),
    path('minutes_business', MinutesBusinessView.as_view(), name='minutes_business'),
    path('minutes_business/<int:business_id>', MinutesBusinessView.as_view(), name='minutes_business'),
    path('minutes_business_update', MinutesBusinessUpdateView.as_view(), name='minutes_business_update'),
    path('minutes_business_update/<int:update_id>', MinutesBusinessUpdateView.as_view(), name='minutes_business_update'),
    path('minutes_form', MinutesFormView.as_view(), name='minutes_form'),
    path('minutes_form/<int:minutes_id>', MinutesFormView.as_view(), name='minutes_form'),
    path('minutes_report', MinutesReportView.as_view(), name='minutes_report'),
    path('minutes_report/<int:report_id>', MinutesReportView.as_view(), name='minutes_report'),
    # path('process_payment/<str:message>/', ProcessPaymentView.as_view(), name='process_payment'),
]