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
        path('class_registered_table', ClassRegisteredTable.as_view(), name='class_registered_table'),
        path('class_registration', ClassRegistrationView.as_view(), name='class_registration'),
        path('costs/<int:cost_id>', CostsView.as_view(), name='costs'),
        path('costs', CostsView.as_view(), name='costs'),
        path('payment', PaymentView.as_view(), name='payment'),
        path('process_payment', ProcessPaymentView.as_view(), name='process_payment'),
        path('process_payment/<str:message>/', ProcessPaymentView.as_view(), name='process_payment'),
        path('profile', ProfileView.as_view(), name='profile'),
        path('search', SearchView.as_view(), name='search'),
        path('student_register', StudentFamilyRegisterView.as_view(), name='student_register'),
        path('unregister_class', UnregisterView.as_view(), name='unregister_class'),
]
