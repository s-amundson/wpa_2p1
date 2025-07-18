from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from ..models import Faq
from ..forms import FaqForm, FaqFilterForm, FaqSearchForm
from src.mixin import BoardMixin

import logging
logger = logging.getLogger(__name__)


class FaqFormView(BoardMixin, FormView):
    model = Faq
    form_class = FaqForm
    template_name = 'student_app/form_as_p.html'
    faq = None
    success_url = reverse_lazy('info:faq')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.faq:
            kwargs['instance'] = self.faq
        return kwargs

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        form.save()
        return super().form_valid(form)

    def test_func(self):
        if self.kwargs.get('faq_id', None) is not None:
            self.faq = get_object_or_404(Faq, pk=self.kwargs['faq_id'])
        return super().test_func()


class FaqList(ListView):
    """
    Return all posts that are with status 1 (published) and order from the latest one.
    """
    model = Faq
    template_name = 'info/faq_list.html'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form'] = FaqFilterForm(initial=self.request.GET)
        context['search_form'] = FaqSearchForm(initial=self.request.GET)
        return context

    def get_queryset(self):
        form = FaqFilterForm(self.request.GET)
        object_list = self.model.objects.filter(status=1)
        if form.is_valid():
            if form.cleaned_data['category'] is not None:
                object_list = object_list.filter(category=form.cleaned_data['category'])
        else:
            logger.warning(form.errors)
        search_form = FaqSearchForm(self.request.GET)
        if search_form.is_valid():
            object_list = object_list.filter(Q(question__icontains=search_form.cleaned_data['search']) |
                                             Q(answer__icontains=search_form.cleaned_data['search']))
        return object_list.order_by('-created_at')
