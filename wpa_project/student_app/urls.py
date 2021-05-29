from django.urls import path, include
from .views import AddStudentView, IndexView, ProfileView, StudentRegisterView
app_name = 'registration'
urlpatterns = [
        path('', IndexView.as_view()),
        path('profile', ProfileView.as_view(), name='profile'),
        path('student_register', StudentRegisterView.as_view(), name='student_register'),
        path('add_student', AddStudentView.as_view(), name='add_student'),
        # path('register/', SignupView.as_view(), name="register"),
        # path('users/', UserList.as_view()),
        # path('users/<pk>/', UserDetails.as_view()),
        # path('groups/', GroupList.as_view()),

]