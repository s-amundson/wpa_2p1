import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.views.generic.base import View

logger = logging.getLogger(__name__)


class StudentList(UserPassesTestMixin, View):
    def get(self, request):
        return render(request, 'student_app/student_list.html')

    def test_func(self):
        return self.request.user.is_board