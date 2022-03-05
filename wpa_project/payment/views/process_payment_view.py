import logging
import uuid
from django.conf import settings
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from ..src.square_helper import SquareHelper

logger = logging.getLogger(__name__)


class ProcessPaymentView(LoginRequiredMixin, View):
    """Shows a payment page for making purchases"""
    donation = False

    def bypass_payment(self, request, table_rows):
        sh = SquareHelper()
        square_response = sh.comp_response(table_rows['note'], table_rows['total'])
        sh.log_payment(request, square_response, create_date=datetime.now())
        return render(request, 'student_app/message.html', {'message': 'No payment needed, Thank You'})

    def get(self, request):
        paydict = {}
        if settings.SQUARE_CONFIG['environment'] == "production":   # pragma: no cover
            paydict['pay_url'] = "https://web.squarecdn.com/v1/square.js"
        else:  # pragma: no cover
            paydict['pay_url'] = "https://sandbox.web.squarecdn.com/v1/square.js"
        paydict['app_id'] = settings.SQUARE_CONFIG['application_id']
        paydict['location_id'] = settings.SQUARE_CONFIG['location_id']
        paydict['action_url'] = request.session.get('action_url', reverse('payment:payment'))
        # rows, total = self.table_rows(request.session)
        table_rows = self.table_rows(request.session)
        logging.debug(table_rows['total'])
        # if table_rows['total'] == 0:
            # No payment necessary
            # self.bypass_payment(request, table_rows)
        bypass = False
        if request.user.is_board and not request.session.get('payment', False):
            bypass = True
        logging.debug(paydict)
        message = request.session.get('message', '')
        context = {'paydict': paydict, 'rows': table_rows['rows'], 'total': table_rows['total'],
                   'bypass': bypass, 'message': message, 'donation': self.donation}
        return render(request, 'payment/square_pay.html', context)

    def table_rows(self, session):
        rows = []
        total = 0
        note = ""
        if 'line_items' in session:
            for row in session['line_items']:
                d = {'name': row['name'], 'quantity': int(row['quantity']),
                     'amount_each': int(row['base_price_money']['amount']) / 100,
                     'amount_total': int(row['base_price_money']['amount']) * int(row['quantity']) / 100}
                logging.debug(f"amount {row['base_price_money']['amount']}, {int(row['base_price_money']['amount'])}")
                rows.append(d)
                total += int(d['amount_total'])
                note += row['name']

        return {'rows': rows, 'total': total, 'note': note}

    def post(self, request):
        logging.debug(request.POST)
        idempotency_key = request.session.get('idempotency_key', None)
        sq_token = request.POST.get('sq_token', None)
        logging.debug(f'uuid = {idempotency_key}, sq_token = {sq_token}')
        request.session['message'] = ''
        if request.session.get('line_items', None) is None:
            logging.debug('missing line items.')
            return render(request, 'student_app/message.html', {'message': 'payment processing error'})
        # get the amount form the line items
        # also get line item name and add to notes
        table_rows = self.table_rows(request.session)

        if request.POST.get('bypass', None) is not None:
            return self.bypass_payment(request, table_rows)

        else:  # pragma: no cover
            logging.debug('payment processing error')
            return render(request, 'student_app/message.html', {'message': 'payment processing error'})


class DonationView(ProcessPaymentView):
    """A view to make it possible for a student to make a stand alone donation."""
    def get(self, request):
        request.session['idempotency_key'] = str(uuid.uuid4())
        request.session['line_items'] = []
        request.session['db'] = None
        self.donation = True
        return super().get(request)
