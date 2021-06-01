from django.urls import path
from .views import *
app_name = 'registration'
urlpatterns = [
        path('', IndexView.as_view(), name='index'),
        path('add_student/<int:student_id>/', AddStudentView.as_view(), name='add_student'),
        path('add_student', AddStudentView.as_view(), name='add_student'),
        path('beginner_class/<int:beginner_class>/', BeginnerClassView.as_view(), name='beginner_class'),
        path('beginner_class', BeginnerClassView.as_view(), name='beginner_class'),
        path('class_list', BeginnerClassListView.as_view(), name='class_list'),
        path('class_registration', ClassRegistrationView.as_view(), name='class_registration'),
        path('profile', ProfileView.as_view(), name='profile'),
        path('student_register', StudentRegisterView.as_view(), name='student_register'),
]