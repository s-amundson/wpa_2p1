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
    instance = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['collections'] = Collections.objects.filter(correction__isnull=True).order_by('-collected_date')
        if 'pk' in self.kwargs:
            context['correction'] = Collections.objects.filter(correction=self.kwargs.get('pk')).last()
        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        if 'pk' in self.kwargs:
            kwargs['instance'] = self.instance = get_object_or_404(Collections, pk=self.kwargs.get('pk'))
        logger.warning(kwargs)
        return kwargs

    def form_invalid(self, form):  # pragma: no cover
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        if 'pk' in self.kwargs and self.has_correction(form):
            instance = Collections.objects.get(pk=self.kwargs.pop('pk'))
            new_form = self.get_form()
            collection = new_form.save()
            instance.correction = collection.id
            instance.save()
            return super().form_valid(new_form)
        else:
            form.save()
            # pass
        return super().form_valid(form)

    def has_correction(self, form):
        fields = ['collected_date', 'cash','treasurer', 'board_member']
        for field in fields:
            if field in form.changed_data:
                return True
        return False