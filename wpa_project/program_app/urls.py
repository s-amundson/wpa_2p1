from django.urls import path
from .views import *
app_name = 'programs'
urlpatterns = [
    path('beginner_class/<int:beginner_class>/', BeginnerClassView.as_view(), name='beginner_class'),
    path('beginner_class/', BeginnerClassView.as_view(), name='beginner_class'),
    path('class_attend/<int:registration>/', ClassAttendView.as_view(), name='class_attend'),
    path('class_attend_list/<int:beginner_class>/', ClassAttendListView.as_view(), name='class_attend_list'),
    path('class_calendar/<int:month>/', ClassCalendarView.as_view(), name='class_calendar'),
    path('class_calendar/', ClassCalendarView.as_view(), name='class_calendar'),
    path('class_list/<int:past>/', BeginnerClassListView.as_view(), name='class_list'),
    path('class_list/', BeginnerClassListView.as_view(), name='class_list'),
    # path('class_payment/', PaymentView.as_view(), name='class_payment'),
    path('class_registered_table/', ClassRegisteredTable.as_view(), name='class_registered_table'),
    path('class_registration_admin/<int:family_id>/', ClassRegistrationAdminView.as_view(), name='class_registration_admin'),
    path('class_registration_admin_list/', AdminRegistrationListView.as_view(), name='class_registration_admin_list'),
    path('class_registration/', ClassRegistrationView.as_view(), name='class_registration'),
    path('class_sign_in/<int:reg_id>/', ClassSignInView.as_view(), name='class_sign_in'),
    path('class_status/<str:class_id>/', ClassStatusView.as_view(), name='class_status'),
    path('class_status/', ClassStatusView.as_view(), name='class_status'),
    path('resume_registration/<int:reg_id>/', ResumeRegistrationView.as_view(), name='resume_registration'),
    path('send_email/', SendEmailView.as_view(), name='send_email'),
    path('send_email/<int:beginner_class>/', SendEmailView.as_view(), name='send_email'),
    path('staff_attendance/', StaffReportView.as_view(), name='staff_attendance'),
    path('unregister_class/', UnregisterView.as_view(), name='unregister_class'),
]
