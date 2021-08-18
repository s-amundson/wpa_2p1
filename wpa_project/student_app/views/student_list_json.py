import logging
from datetime import timedelta
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render, get_list_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic import ListView
from django.utils import timezone
# from django.db.models import model
# from django.core.exceptions import ObjectDoesNotExist

from ..forms import BeginnerClassForm, ClassAttendanceForm
from ..models import Student, BeginnerClass, ClassRegistration, CostsModel
# from payment.src import SquareHelper

logger = logging.getLogger(__name__)

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape


class StudentListJson(UserPassesTestMixin, BaseDatatableView):
    # The model we're going to show
    model = Student

    # define the columns that will be returned
    columns = ['last_name', 'first_name', 'dob', 'safety_class']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['last_name', 'first_name', 'dob', 'safety_class']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    # def render_column(self, row, column):
    #     # We want to render user as a custom column
    #     if column == 'user':
    #         # escape HTML for security reasons
    #         return escape('{0} {1}'.format(row.customer_firstname, row.customer_lastname))
    #     else:
    #         return super(OrderListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            # qs = qs.filter(first_name__istartswith=search, last_name__istartswith=search)
            qs = qs.filter(Q(first_name__istartswith=search) | Q(last_name__istartswith=search))


        return qs

    def test_func(self):
        return self.request.user.is_board
