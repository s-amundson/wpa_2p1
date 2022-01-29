from django.urls import path
from .views import *
app_name = 'joad'
urlpatterns = [
    path('attend/<int:class_id>/', AttendView.as_view(), name='attend'),
    path('attendance/<int:class_id>/', AttendanceListView.as_view(), name='attendance'),
    path('attendance/', AttendanceListView.as_view(), name='attendance'),
    path('class_list/<int:session_id>/', ClassListView.as_view(), name='class_list'),
    path('class_list/', ClassListView.as_view(), name='class_list'),
    path('event/<int:event_id>/', JoadEventView.as_view(), name='event'),
    path('event/', JoadEventView.as_view(), name='event'),
    path('event_attendance/<int:event_id>/<int:student_id>/', EventAttendanceView.as_view(), name='event_attendance'),
    path('event_registration/<int:event_id>/', EventRegistrationView.as_view(), name='event_registration'),
    path('event_registration/', EventRegistrationView.as_view(), name='event_registration'),
    path('index/', IndexView.as_view(), name='index'),
    path('joad_class/<int:class_id>/', JoadClassView.as_view(), name='joad_class'),
    path('joad_class/', JoadClassView.as_view(), name='joad_class'),
    path('pin_score/<int:score_id>/', PinScoreView.as_view(), name='pin_score'),
    path('pin_score/', PinScoreView.as_view(), name='pin_score'),
    path('pin_score_list/', PinScoreListView.as_view(), name='pin_score_list'),
    path('registration/<int:session_id>/', RegistrationView.as_view(), name='registration'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('session/<int:session_id>/', SessionFormView.as_view(), name='session'),
    path('session', SessionFormView.as_view(), name='session'),
    path('waiver/<int:student_id>/', WaiverView.as_view(), name='waiver')
]
