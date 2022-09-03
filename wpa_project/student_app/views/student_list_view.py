import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.list import ListView
from ..forms import SearchColumnsForm
from ..models import Student
logger = logging.getLogger(__name__)


class StudentList(UserPassesTestMixin, ListView):
    model = Student
    paginate_by = 100  # if pagination is desired
    form_class = SearchColumnsForm
    form = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(initial=self.request.GET)
        return context

    def get_queryset(self):
        self.form = self.form_class(self.request.GET)
        object_list = self.model.objects.filter(student_family__isnull=False)
        if self.form.is_valid():
            if self.form.cleaned_data['safety_class']:
                object_list = object_list.filter(safety_class__isnull=False)
            if self.form.cleaned_data['last_name']:
                object_list = object_list.filter(last_name__icontains=self.form.cleaned_data['last_name'])
            if self.form.cleaned_data['first_name']:
                object_list = object_list.filter(first_name__icontains=self.form.cleaned_data['first_name'])
            if self.form.cleaned_data['staff']:
                object_list = object_list.filter(user__is_staff=True)
        return object_list.order_by('last_name')

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        else:
            return False
