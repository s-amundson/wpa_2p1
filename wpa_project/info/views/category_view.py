import logging
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.base import View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from ..forms import CategoryForm
from ..models import Category
from src.mixin import BoardMixin

logger = logging.getLogger(__name__)


class CategoryDeleteView(BoardMixin, View):
    def post(self, request, category_id):
        category = get_object_or_404(Category, pk=category_id)
        category.delete()
        return HttpResponseRedirect(reverse_lazy('info:category_list'))


class CategoryListView(BoardMixin, ListView):
    model = Category
    paginate_by = 100  # if pagination is desired
    queryset = Category.objects.all().order_by('title')


class CategoryView(BoardMixin, FormView):
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
