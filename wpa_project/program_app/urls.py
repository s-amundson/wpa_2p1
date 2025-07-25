from django.urls import path
from .views import *
app_name = 'programs'
urlpatterns = [
    path('admit_wait/<int:event>/', AdmitWaitView.as_view(), name='admit_wait'),
    path('admit_wait/<int:event>/<int:family_id>/', AdmitWaitView.as_view(), name='admit_wait'),
    path('beginner_class/<int:beginner_class>/', BeginnerClassView.as_view(), name='beginner_class'),
    path('beginner_class/', BeginnerClassView.as_view(), name='beginner_class'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('calendar/<int:year>/<int:month>/', CalendarView.as_view(), name='calendar'),
    path('class_list/<int:past>/', BeginnerClassListView.as_view(), name='class_list'),
    path('class_list/', BeginnerClassListView.as_view(), name='class_list'),
    path('class_registration_admin/<int:family_id>/', ClassRegistrationAdminView.as_view(), name='class_registration_admin'),
    path('class_registration_admin_list/', AdminRegistrationListView.as_view(), name='class_registration_admin_list'),
    path('class_registration/<int:event>/', ClassRegistrationView.as_view(), name='class_registration'),
    path('class_registration/', ClassRegistrationView.as_view(), name='class_registration'),
    path('class_sign_in/<int:reg_id>/', ClassSignInView.as_view(), name='class_sign_in'),
    path('class_status/<str:class_id>/', ClassStatusView.as_view(), name='class_status'),
    path('class_status/', ClassStatusView.as_view(), name='class_status'),
    path('google_calendar/', EventCalendarView.as_view(), name='google_calendar'),
    path('history/', HistoryView.as_view(), name='history'),
    path('history/<int:family_id>/', HistoryView.as_view(), name='history'),
    path('resume_registration/<int:reg_id>/', ResumeRegistrationView.as_view(), name='resume_registration'),
    path('send_email/', SendEmailView.as_view(), name='send_email'),
    path('send_email/<int:beginner_class>/', SendEmailView.as_view(), name='send_email'),
    path('staff_attendance/', StaffReportView.as_view(), name='staff_attendance'),
    path('staff_point_hisotry/<int:student>/', StaffPointHistoryView.as_view(), name='staff_point_history'),
    path('wait_list/<int:event>/', WaitListView.as_view(), name='wait_list'),
]
