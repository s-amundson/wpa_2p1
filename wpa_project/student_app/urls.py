from django.urls import path, include
from .views import AddStudentView, IndexView, ProfileView, StudentRegisterView
app_name = 'registration'
urlpatterns = [
        path('', IndexView.as_view()),
        path('profile', ProfileView.as_view(), name='profile'),
        path('student_register', StudentRegisterView.as_view(), name='student_register'),
        path('add_student/<int:goal_id>/', AddStudentView.as_view(), name='add_student'),
        path('add_student', AddStudentView.as_view(), name='add_student'),

]