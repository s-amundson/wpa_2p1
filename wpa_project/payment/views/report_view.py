import logging
from django.views.generic import FormView
from django.urls import reverse_lazy

from ..forms import ReportForm
from ..models import PaymentLog
from src.mixin import BoardMixin
logger = logging.getLogger(__name__)


class ReportView(BoardMixin, FormView):
    categories = ['donation', 'intro', 'joad', 'membership']
    form_class = ReportForm
    model = PaymentLog
    success_url = reverse_lazy('payment:report')
    template_name = 'payment/report.html'

    def form_valid(self, form):
        form.beginning_date = form.cleaned_data.get('beginning_date', form.beginning_date)
        form.end_date = form.cleaned_data.get('end_date', form.end_date)
        form.get_results()
        return self.form_invalid(form)
