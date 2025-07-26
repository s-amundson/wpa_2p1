import logging

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from ..models import Bow, BowInventory
from ..forms import BowForm, BowInventoryForm
from src.mixin import StaffMixin
logger = logging.getLogger(__name__)


class BowFormView(StaffMixin, FormView):
    model = Bow
    form_class = BowForm
    template_name = 'student_app/form_as_p.html'
    success_url = reverse_lazy('inventory:bow_list')

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.debug(form.cleaned_data)
        b = form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'pk' in self.kwargs:
            kwargs['instance'] = get_object_or_404(Bow, pk=self.kwargs.get('pk'))
        return kwargs

class BowListView(StaffMixin, ListView):
    model = Bow
    template_name = 'inventory/bow_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['in_service'] = self.kwargs.get('in_service', False)
        return context

    def get_queryset(self):
        logger.debug(self.request.GET)
        object_list = self.model.objects.all()
        return object_list.order_by('bow_id')


class BowInventoryView(StaffMixin, FormView):
    model = Bow
    form_class = BowInventoryForm
    template_name = 'inventory/barcode.html'
    success_url = reverse_lazy('inventory:bow_inventory')

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.debug(form.cleaned_data)
        b = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = BowInventory.objects.filter(user=self.request.user).order_by('-inventory_date')[:10]
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial']['user'] = self.request.user
        return kwargs