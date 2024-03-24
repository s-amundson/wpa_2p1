from django.urls import path
from .views import *
app_name = 'payment'
urlpatterns = [
    path('card_default/<int:card_id>/', CardDefaultView.as_view(), name='card_default'),
    path('card_manage/', CardManageView.as_view(), name='card_manage'),
    path('card_remove/', CardRemoveView.as_view(), name='card_remove'),
    path('card_remove/<int:card_id>/', CardRemoveView.as_view(), name='card_remove'),
    path('make_payment/', CreatePaymentView.as_view(), name='make_payment'),
    path('reimbursement_form/', ReimbursementFormView.as_view(), name='reimbursement_form'),
    path('reimbursement_form/<int:pk>/', ReimbursementFormView.as_view(), name='reimbursement_form'),
    path('reimbursement_list/', ReimbursementListView.as_view(), name='reimbursement_list'),
    path('reimbursement_vote/<int:pk>/', ReimbursementVoteView.as_view(), name='reimbursement_vote'),
    path('report', ReportView.as_view(), name='report'),
    path('view_payment/<pk>/', PaymentView.as_view(), name='view_payment'),
]
