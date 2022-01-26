from django.urls import path
from .views import *
app_name = 'joad'
urlpatterns = [
    path('attend/<int:class_id>', AttendView.as_view(), name='attend'),
    path('attendance/<int:class_id>', AttendanceListView.as_view(), name='attendance'),
    path('attendance/', AttendanceListView.as_view(), name='attendance'),
    path('class_list/<int:session_id>', ClassListView.as_view(), name='class_list'),
    path('class_list/', ClassListView.as_view(), name='class_list'),
    path('index/', IndexView.as_view(), name='index'),
    path('joad_class/<int:class_id>', JoadClassView.as_view(), name='joad_class'),
    path('joad_class/', JoadClassView.as_view(), name='joad_class'),
    path('registration/<int:session_id>', RegistrationView.as_view(), name='registration'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('session/<int:session_id>', SessionFormView.as_view(), name='session'),
    path('session', SessionFormView.as_view(), name='session'),
    path('waiver/<int:student_id>', WaiverView.as_view(), name='waiver')
]
