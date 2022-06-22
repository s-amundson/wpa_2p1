from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView

from ..forms import CardRemoveForm
from ..models import Card
from ..src import CardHelper

import logging
logger = logging.getLogger(__name__)


class CardRemoveView(LoginRequiredMixin, FormView):
    template_name = 'student_app/form_as_p.html'
    form_class = CardRemoveForm
    success_url = reverse_lazy('registration:index')

    def form_invalid(self, form):
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        try:
            card = Card.objects.get(pk=form.cleaned_data['card'])
        except Card.model.DoesNotExist:
            return self.form_invalid(form)
        card_helper = CardHelper(card)
        if card_helper.disable_card() is not None:
            return super().form_valid(form)
        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
