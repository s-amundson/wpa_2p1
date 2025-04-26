from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView
from ..forms import CollectionForm
from ..models import Collections
from src.mixin import BoardMixin

import logging
logger = logging.getLogger(__name__)


class CollectionView(BoardMixin, FormView):
    template_name = 'payment/collection.html'
    form_class = CollectionForm
    success_url = reverse_lazy('payment:collections')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['collections'] = Collections.objects.all().order_by('-collected_date')
        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        if 'pk' in self.kwargs:
            kwargs['instance'] = get_object_or_404(Collections, pk=self.kwargs.get('pk'))
        logger.warning(kwargs)
        return kwargs

    def form_invalid(self, form):  # pragma: no cover
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
