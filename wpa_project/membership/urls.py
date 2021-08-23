from django.urls import path
from .views import *
app_name = 'membership'
urlpatterns = [
    path('level/<int:level_id>', LevelView.as_view(), name='level'),
    path('level', LevelView.as_view(), name='level'),
    path('level_api', LevelApiView.as_view(), name='level_api'),
    path('membership', MembershipView.as_view(), name='membership'),
    # path('process_payment/<str:message>/', ProcessPaymentView.as_view(), name='process_payment'),
]