from django import forms
from django.utils import timezone
from django.utils.datetime_safe import date
from django.db.models import Sum
from django.conf import settings

from ..models import Card, Customer, PaymentLog
from ..src import CardHelper, CustomerHelper, PaymentHelper

import logging
logger = logging.getLogger(__name__)


class ReportForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.debug(self.initial)
        self.beginning_date = timezone.datetime(2022, 1, 1)
        self.end_date = self.initial.get('end_date', timezone.datetime.today())
        self.fields['beginning_date'] = forms.DateField(
            initial=date(2022, 1, 1),
            widget=forms.SelectDateWidget(years=range(date.today().year, 2021, -1)),
        )
        self.fields['end_date'] = forms.DateField(
            initial=date.today(),
            widget=forms.SelectDateWidget(years=range(date.today().year, 2021, -1)),
        )
        self.categories = ['donation', 'intro', 'joad', 'membership']
        self.result = []
        self.get_results()

    def get_results(self):
        queryset = PaymentLog.objects.filter(checkout_created_time__gte=self.beginning_date)
        queryset = queryset.filter(checkout_created_time__lte=self.end_date)
        self.result = []
        for category in self.categories:
            d = {'name': category}
            q = queryset.filter(category=category)
            transactions = q.filter(status='COMPLETED')
            d['transaction_sum'] = self.get_sum(transactions)
            d['transaction_count'] = transactions.count()
            refunds = q.filter(status='refund')
            d['refund_sum'] = self.get_sum(refunds)
            d['refund_count'] = refunds.count()
            self.result.append(d)
        d = {'name': 'total'}
        transactions = queryset.filter(status='COMPLETED')
        d['transaction_sum'] = self.get_sum(transactions)
        d['transaction_count'] = transactions.count()
        refunds = queryset.filter(status='refund')
        d['refund_sum'] = self.get_sum(refunds)
        d['refund_count'] = refunds.count()
        self.result.append(d)

    def get_sum(self, queryset):
        query_sum = queryset.aggregate(sum=Sum('total_money'))['sum']
        if query_sum is None:
            query_sum = 0
        else:
            query_sum = query_sum / 100  # to change from cents to dollars
        return query_sum
