import uuid
import json

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic.detail import DetailView

from ..forms import PaymentForm
from ..models import Card, PaymentLog

import logging
logger = logging.getLogger(__name__)


class CreatePaymentView(FormView):
    """ Expects line_items and payment_description to be in session, defaults to making a donation if not present.
        line_items = [{'name': <string>, 'quantity': <int>, 'amount_each': <int>}
        description = <string> """
    template_name = 'payment/make_payment.html'
    form_class = PaymentForm
    success_url = reverse_lazy('registration:index')

    def form_invalid(self, form):
        logging.debug(form.cleaned_data)
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        if form.process_payment(self.request.session.get('idempotency_key', str(uuid.uuid4()))):
            if self.request.user.is_authenticated:
                self.success_url = reverse_lazy('payment:view_payment', args=[form.log.id])
            return super().form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if settings.SQUARE_CONFIG['environment'] == "production":   # pragma: no cover
            context['pay_url'] = "https://web.squarecdn.com/v1/square.js"
        else:  # pragma: no cover
            context['pay_url'] = "https://sandbox.web.squarecdn.com/v1/square.js"
        context['app_id'] = settings.SQUARE_CONFIG['application_id']
        context['location_id'] = settings.SQUARE_CONFIG['location_id']
        context['action_url'] = self.request.session.get('action_url', reverse_lazy('payment:make_payment'))
        if self.request.user.is_authenticated:
            context['cards'] = Card.objects.filter(customer__user=self.request.user)
        else:
            context['cards'] = []
        context['url_remove_card'] = reverse_lazy('payment:card_remove')
        logging.debug(context['cards'])
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        items = []
        line_items = self.request.session.get('line_items', [])
        total = 0
        logging.debug(line_items)
        for item in line_items:
            item['total'] = item['quantity'] * item['amount_each']
            total += item['total']
            items.append(json.dumps(item))

        kwargs['description'] = self.request.session.get('payment_description', '')
        kwargs['line_items'] = line_items
        # kwargs['initial']['items'] = json.dumps(line_items)
        kwargs['initial']['amount'] = total
        logging.debug(items)
        return kwargs


class PaymentView(UserPassesTestMixin, DetailView):
    model = PaymentLog
    object = None
    template_name = 'payment/view_payment.html'

    def test_func(self):
        self.object = self.get_object()
        logging.debug(self.object)
        return self.request.user.is_staff or self.object.user == self.request.user
