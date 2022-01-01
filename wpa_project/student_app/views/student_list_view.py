import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.views.generic.base import View
from ..forms import SearchColumnsForm

logger = logging.getLogger(__name__)


class StudentList(UserPassesTestMixin, View):
    all_columns = ['last_name', 'first_name', 'dob', 'safety_class', 'instructor']
    default_columns = {'last_name': True, 'first_name': True, 'dob': False, 'safety_class': True, 'instructor': False}

    def get(self, request):

        search_columns = request.session.get('search_columns', self.default_columns)
        form = SearchColumnsForm(initial=search_columns)

        return render(request, 'student_app/student_list.html',
                      {'form': form, 'columns': self.table_columns(search_columns)})

    def post(self, request):
        logging.debug(request.POST)
        form = SearchColumnsForm(request.POST)
        if form.is_valid():
            logging.debug(form.cleaned_data)
            request.session['search_columns'] = form.cleaned_data
        else:
            logging.debug(form.errors)
        return render(request, 'student_app/student_list.html',
                      {'form': form, 'columns': self.table_columns(form.cleaned_data)})

    def table_columns(self, column_dict):
        columns = column_dict.copy()
        if 'instructor' in columns.keys():
            logging.debug('found instructor')
            columns.pop('instructor')
        else:
            columns
        logging.debug(columns)
        return columns

    def test_func(self):
        return self.request.user.is_board


# class StudentListTable(UserPassesTestMixin, View):
#     def get(self, request):
#         columns = ['last_name', 'first_name', 'dob', 'safety_class']
#         return render(request, 'student_app/student_list.html', {'columns': columns})
#
#     def test_func(self):
#         return self.request.user.is_board