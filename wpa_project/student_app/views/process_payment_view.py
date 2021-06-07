import logging
import uuid
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from square.client import Client
from ..models import ClassRegistration, PaymentLog, StudentFamily
from ..src.square_helper import dummy_response, line_item, log_response

logger = logging.getLogger(__name__)


class ProcessPaymentView(LoginRequiredMixin, View):
    """Shows a payment page for making purchases"""

    def get(self, request):
        # # TODO remove this as it is just to get square working
        # request.session['idempotency_key'] = str(uuid.uuid4())
        # request.session['line_items'] = [line_item(f"Class on None student id: 1", 1, 5), ]

        paydict = {}
        if settings.SQUARE_CONFIG['environment'] == "production":
            # paydict['production'] = True
            paydict['pay_url'] = '' # "https://js.squareup.com/v2/paymentform"
        else:
            # paydict['production'] = False
            paydict['pay_url'] = "https://sandbox.web.squarecdn.com/v1/square.js"  #"https://js.squareupsandbox.com/v2/paymentform"
        paydict['app_id'] = settings.SQUARE_CONFIG['application_id']
        paydict['location_id'] = settings.SQUARE_CONFIG['location_id']
        rows, total = self.table_rows(request.session)
        bypass = False
        if settings.DEBUG or request.user.is_authenticated:
            bypass = True
        logging.debug(paydict)
        message = request.session.get('message', '')
        context = {'paydict': paydict, 'rows': rows, 'total': total, 'bypass': bypass, 'message': message}
        return render(request, 'student_app/square_pay.html', context)

    def table_rows(self, session):
        rows = []
        total = 0
        if 'line_items' in session:
            # line_items = session['line_items']
            for row in session['line_items']:
                d = {'name': row['name'], 'quantity': int(row['quantity']),
                     'amount_each': int(row['base_price_money']['amount']) / 100,
                     'amount_total': int(row['base_price_money']['amount']) * int(row['quantity']) / 100}
                logging.debug(f"amount {row['base_price_money']['amount']}, {int(row['base_price_money']['amount'])}")
                rows.append(d)
                total += int(d['amount_total'])

        return rows, total

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
        amt = 0
        note = ""
        for line in request.session['line_items']:
            amt += line['base_price_money']['amount'] * int(line['quantity'])
            note += f" {line['name']},"

        # Monetary amounts are specified in the smallest unit of the applicable currency.
        amount = {'amount': amt, 'currency': 'USD'}

        if request.POST.get('bypass', None) is not None:
            logging.debug(request.POST.get('bypass', None))
            square_response = dummy_response(note, amount)
            log_response(request, square_response, create_date=datetime.now())
        else:
            logging.debug('payment processing error')
            return render(request, 'student_app/message.html', {'message': 'payment processing error'})
