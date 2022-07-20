import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.utils.datetime_safe import date


from ..forms import ReportForm
from ..models import PaymentLog
logger = logging.getLogger(__name__)


class ReportView(UserPassesTestMixin, FormView):
    categories = ['donation', 'intro', 'joad', 'membership']
    form_class = ReportForm
    model = PaymentLog
    success_url = reverse_lazy('payment:report')
    template_name = 'payment/report.html'

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        form.beginning_date = form.cleaned_data.get('beginning_date', form.beginning_date)
        form.end_date = form.cleaned_data.get('end_date', form.end_date)
        form.get_results()
        return self.form_invalid(form)

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        else:
            return False
