import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.base import View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from ..forms import CategoryForm
from ..models import Category

logger = logging.getLogger(__name__)


class CategoryDeleteView(UserPassesTestMixin, View):
    def post(self, request, category_id):
        category = get_object_or_404(Category, pk=category_id)
        category.delete()
        return HttpResponseRedirect(reverse_lazy('info:category_list'))

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        return False


class CategoryListView(UserPassesTestMixin, ListView):
    model = Category
    paginate_by = 100  # if pagination is desired
    queryset = Category.objects.all().order_by('title')

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        return False


class CategoryView(UserPassesTestMixin, FormView):
    template_name = 'contact_us/category.html'
    form_class = CategoryForm
    success_url = reverse_lazy('info:category_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'category_id' in self.kwargs:
            kwargs['instance'] = get_object_or_404(Category, pk=self.kwargs['category_id'])
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        return False
