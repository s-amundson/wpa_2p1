from django.urls import path
from .views import *
app_name = 'membership'
urlpatterns = [
    path('level/<int:level_id>/', LevelView.as_view(), name='level'),
    path('level/', LevelView.as_view(), name='level'),
    path('election/', ElectionView.as_view(), name='election'),
    path('election/<int:election_id>/', ElectionView.as_view(), name='election'),
    path('election_candidate/<int:election_id>/', ElectionCandidateView.as_view(), name='election_candidate'),
    path('election_list/', ElectionListView.as_view(), name='election_list'),
    path('election_result/<int:election_id>/', ElectionResultView.as_view(), name='election_result'),
    path('election_vote/<int:election_id>/', ElectionVoteView.as_view(), name='election_vote'),
    path('member_list/', MemberList.as_view(), name='member_list'),
    path('membership/', MembershipView.as_view(), name='membership'),
    path('membership/<int:sf_id>/', MembershipView.as_view(), name='membership'),
]