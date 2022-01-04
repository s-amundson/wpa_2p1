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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(initial=self.request.GET)
        return context

    def get_queryset(self):
        form = self.form_class(self.request.GET)
        object_list = self.model.objects.all()
        if form.is_valid():
            logging.debug(form.cleaned_data)
            if form.cleaned_data['safety_class']:
                object_list = object_list.filter(safety_class__isnull=False)
            if form.cleaned_data['last_name']:
                logging.debug(form.cleaned_data['last_name'])
                object_list = object_list.filter(last_name__icontains=form.cleaned_data['last_name'])
            if form.cleaned_data['first_name']:
                logging.debug(form.cleaned_data['first_name'])
                object_list = object_list.filter(first_name__icontains=form.cleaned_data['first_name'])
            if form.cleaned_data['instructor']:
                object_list = object_list.filter(user__is_instructor=True)
        return object_list

    def test_func(self):
        return self.request.user.is_board
