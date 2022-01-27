import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.base import View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from allauth.account.models import EmailAddress
from ..forms import CategoryForm
from ..models import Category
from student_app.models import Student
logger = logging.getLogger(__name__)


class CategoryDeleteView(UserPassesTestMixin, View):
    def post(self, request, category_id):
        category = get_object_or_404(Category, pk=category_id)
        category.delete()

    def test_func(self):
        return self.request.user.is_board


class CategoryListView(UserPassesTestMixin, ListView):
    model = Category
    paginate_by = 100  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = []
        for c in self.object_list:
            r = []
            for u in c.recipients.all():
                s = u.student_set.first()
                logging.debug(s)
                r.append(f'{s.first_name} {s.last_name}')
            categories.append({'id': c.id, 'title': c.title, 'recipients': r})
        context['categories'] = categories
        return context

    def test_func(self):
        return self.request.user.is_board


class CategoryView(UserPassesTestMixin, FormView):
    template_name = 'contact_us/message.html'
    form_class = CategoryForm
    success_url = reverse_lazy('contact_us:category_list')

    def get_form(self):
        try:
            category_id = self.kwargs['category_id']
        except KeyError:
            category_id = None
        logging.debug(category_id)
        if category_id is not None:
            return self.form_class(instance=get_object_or_404(Category, pk=category_id))
        return self.form_class()

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        form.save()
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_board