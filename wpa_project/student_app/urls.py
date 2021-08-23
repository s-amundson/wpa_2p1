from django.urls import path
from .views import *
app_name = 'registration'
urlpatterns = [
        path('', IndexView.as_view(), name='index'),
        path('add_student/<int:student_id>/', AddStudentView.as_view(), name='add_student'),
        path('add_student', AddStudentView.as_view(), name='add_student'),
        path('privacy', PrivacyView.as_view(), name='privacy'),
        path('profile', ProfileView.as_view(), name='profile'),
        path('search', SearchView.as_view(), name='search'),
        path('student_api/<int:student_id>/', StudentApiView.as_view(), name='student_api'),
        path('student_api', StudentApiView.as_view(), name='student_api'),
        path('student_family_api/<int:family_id>/', StudentFamilyApiView.as_view(), name='student_family_api'),
        path('student_family_api', StudentFamilyApiView.as_view(), name='student_family_api'),
        path('student_list', StudentList.as_view(), name='student_list'),
        path('student_list_json', StudentListJson.as_view(), name='student_list_json'),
        path('student_register/<int:family_id>/', StudentFamilyRegisterView.as_view(), name='student_register'),
        path('student_register', StudentFamilyRegisterView.as_view(), name='student_register'),
        path('student_table', StudentTableView.as_view(), name='student_table'),
        path('terms', TermsView.as_view(), name='terms'),
        path('theme', ThemeView.as_view(), name='theme'),
]
