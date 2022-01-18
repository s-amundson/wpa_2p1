from django.urls import path
from .views import *
app_name = 'joad'
urlpatterns = [
    path('joad_class/<int:class_id>', JoadClassView.as_view(), name='joad_class'),
    path('joad_class/', JoadClassView.as_view(), name='joad_class'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('session/<int:session_id>', SessionFormView.as_view(), name='session'),
    path('session', SessionFormView.as_view(), name='session'),
    # path('level_api', LevelApiView.as_view(), name='level_api'),
    # path('membership', MembershipView.as_view(), name='membership'),
    # path('membership/<int:sf_id>', MembershipView.as_view(), name='membership'),
]
