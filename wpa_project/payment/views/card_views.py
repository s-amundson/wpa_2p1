from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, View
from django.http import HttpResponseRedirect
from django.conf import settings

from ..forms import CardNewForm, CardRemoveForm
from ..models import Card, Customer
from ..src import CardHelper, CustomerHelper

import logging
logger = logging.getLogger(__name__)


class CardManageView(LoginRequiredMixin, FormView):
    template_name = 'payment/cards.html'
    form_class = CardNewForm
    success_url = reverse_lazy('payment:card_manage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if settings.SQUARE_CONFIG['environment'] == "production":   # pragma: no cover
            context['pay_url'] = "https://web.squarecdn.com/v1/square.js"
        else:  # pragma: no cover
            context['pay_url'] = "https://sandbox.web.squarecdn.com/v1/square.js"
        context['cards'] = Card.objects.filter(customer__user=self.request.user, enabled=True)
        context['app_id'] = settings.SQUARE_CONFIG['application_id']
        context['location_id'] = settings.SQUARE_CONFIG['location_id']
        context['action_url'] = self.request.session.get('action_url', reverse_lazy('payment:make_payment'))
        return context

    def form_valid(self, form):
        # logging.debug(form.cleaned_data)
        card_helper = CardHelper()
        customer = Customer.objects.filter(user=self.request.user).last()
        if customer is None:
            ch = CustomerHelper(self.request.user)
            customer = ch.create_customer()
        if customer is not None:
            card = card_helper.create_card_from_source(customer, form.cleaned_data['source_id'])
            if card is not None:
                return super().form_valid(form)
        # logging.debug(card_helper.errors)
        for error in card_helper.errors:
            form.card_errors.append(error)
        return super().form_invalid(form)


class CardRemoveView(LoginRequiredMixin, FormView):
    template_name = 'payment/remove_card.html'
    form_class = CardRemoveForm
    success_url = reverse_lazy('registration:index')

    def form_invalid(self, form):
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        # logging.debug(form.cleaned_data)
        try:
            card = Card.objects.get(pk=form.cleaned_data['card'])
        except Card.model.DoesNotExist:  # pragma: no cover
            return self.form_invalid(form)
        card_helper = CardHelper(card)
        if card_helper.disable_card() is not None:
            return super().form_valid(form)
        return self.form_invalid(form)  # pragma: no cover

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
