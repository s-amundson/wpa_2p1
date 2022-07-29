from django.urls import path
from .views import *
app_name = 'membership'
urlpatterns = [
    path('level/<int:level_id>/', LevelView.as_view(), name='level'),
    path('level/', LevelView.as_view(), name='level'),
    path('member_list/', MemberList.as_view(), name='member_list'),
    path('membership/', MembershipView.as_view(), name='membership'),
    path('membership/<int:sf_id>/', MembershipView.as_view(), name='membership'),
]