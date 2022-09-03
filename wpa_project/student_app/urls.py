from django.urls import path
from .views import *
app_name = 'registration'
urlpatterns = [
        path('', IndexView.as_view(), name='index'),
        path('add_student/<int:student_id>/', AddStudentView.as_view(), name='add_student'),
        path('add_student/', AddStudentView.as_view(), name='add_student'),
        path('covid_vax/<int:student_id>/', CovidVaxView.as_view(), name='covid_vax'),
        path('instructor_update/', InstructorUpdateView.as_view(), name='instructor_update'),
        path('is_joad/<int:student_id>/', StudentIsJoadView.as_view(), name='is_joad'),
        path('pdf/<int:student_id>/', PdfGetView.as_view(), name='pdf'),
        path('policy/<str:policy>/', PolicyView.as_view(), name='policy'),
        path('profile/', ProfileView.as_view(), name='profile'),
        path('search/', SearchEmailView.as_view(), name='search'),
        path('search_name/', SearchNameView.as_view(), name='search_name'),
        path('search_phone/', SearchPhoneView.as_view(), name='search_phone'),
        path('search_result/', SearchResultView.as_view(), name='search_result'),
        path('search_result/<int:student_family>/', SearchResultView.as_view(), name='search_result'),
        path('search_result_list/', SearchResultListView.as_view(), name='search_result_list'),
        path('send_email/', SendEmailView.as_view(), name='send_email'),
        path('student_family/<int:family_id>/', StudentFamilyView.as_view(), name='student_family'),
        path('student_family/', StudentFamilyView.as_view(), name='student_family'),
        path('student_list/', StudentList.as_view(), name='student_list'),
        path('student_table/', StudentTableView.as_view(), name='student_table'),
        path('terms/', TermsView.as_view(), name='terms'),
        path('theme/', ThemeView.as_view(), name='theme'),
        path('update_user/<int:user_id>/', UserView.as_view(), name='update_user'),
        path('waiver/<int:student_id>/', WaiverView.as_view(), name='waiver'),
        path('waiver_recreate/<int:student_id>/', WaiverRecreateView.as_view(), name='waiver_recreate')
]
