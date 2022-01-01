import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

from ..models import Student

logger = logging.getLogger(__name__)


class StudentListJson(UserPassesTestMixin, BaseDatatableView):
    # The model we're going to show
    model = Student

    # define the columns that will be returned
    # columns = ['last_name', 'first_name', 'dob', 'safety_class']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    # order_columns = ['last_name', 'first_name', 'dob', 'safety_class']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500
    default_columns = {'last_name': True, 'first_name': True, 'dob': False, 'safety_class': True,
                       'instructor': False}
    # def render_column(self, row, column):
    #     # We want to render user as a custom column
    #     if column == 'instructor':
    #         # escape HTML for security reasons
    #         instructor = False
    #         if row.user is not None:
    #             instructor = row.user.is_instructor
    #         logging.debug(instructor)
    #         return escape(instructor)
    #     else:
    #         return super(StudentListJson, self).render_column(row, column)

    def get_columns(self):

        column_dict = self.request.session.get('search_columns', self.default_columns)
        self.columns = []
        self.order_columns = []
        for k,v in column_dict.items():
            if v:
                if k != 'instructor':
                    self.columns.append(k)
                    self.order_columns.append(k)
        return self.columns

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        column_dict = self.request.session.get('search_columns', self.default_columns)
        if column_dict['instructor']:
            return Student.objects.filter(user__is_instructor=True)
        else:
            return Student.objects.all()

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(first_name__istartswith=search) | Q(last_name__istartswith=search))
        return qs

    def test_func(self):
        return self.request.user.is_board
