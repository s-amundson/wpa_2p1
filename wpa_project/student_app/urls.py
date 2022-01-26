from django.urls import path
from .views import *
app_name = 'registration'
urlpatterns = [
        path('', IndexView.as_view(), name='index'),
        path('add_student/<int:student_id>/', AddStudentView.as_view(), name='add_student'),
        path('add_student/', AddStudentView.as_view(), name='add_student'),
        path('covid_vax/<int:student_id>/', CovidVaxView.as_view(), name='covid_vax'),
        path('help/', HelpView.as_view(), name='help'),
        path('instructor_update/', InstructorUpdateView.as_view(), name='instructor_update'),
        path('pdf/<int:student_id>/', PdfGetView.as_view(), name='pdf'),
        path('policy/<str:policy>/', PolicyView.as_view(), name='policy'),
        path('profile/', ProfileView.as_view(), name='profile'),
        path('search/', SearchView.as_view(), name='search'),
        path('search_result/<int:student_family>', SearchResultView.as_view(), name='search_result'),
        path('student_api/<int:student_id>/', StudentApiView.as_view(), name='student_api'),
        path('student_api/', StudentApiView.as_view(), name='student_api'),
        path('student_family_api/<int:family_id>/', StudentFamilyApiView.as_view(), name='student_family_api'),
        path('student_family_api/', StudentFamilyApiView.as_view(), name='student_family_api'),
        path('student_list/', StudentList.as_view(), name='student_list'),
        path('student_register/<int:family_id>/', StudentFamilyRegisterView.as_view(), name='student_register'),
        path('student_register/', StudentFamilyRegisterView.as_view(), name='student_register'),
        path('student_table/', StudentTableView.as_view(), name='student_table'),
        path('terms/', TermsView.as_view(), name='terms'),
        path('theme/', ThemeView.as_view(), name='theme'),
        path('update_user/<int:user_id>/', UserView.as_view(), name='update_user')
]
