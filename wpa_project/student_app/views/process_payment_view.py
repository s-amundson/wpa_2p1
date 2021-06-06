import logging
import uuid
from datetime import timedelta
from django.conf import settings
from django.shortcuts import render
from django.utils.datetime_safe import date
from django.views.generic.base import View
from square.client import Client
from ..models import ClassRegistration, PaymentLog, StudentFamily
from ..src.square_helper import line_item
#
# from registration.models import Joad_session_registration, Member, Payment_log, Membership
# from registration.src.Email import Email

logger = logging.getLogger(__name__)


class ProcessPaymentView(View):
    """Shows a payment page for making purchases"""

    def get(self, request):
        # TODO remove this as it is just to get square working
        request.session['idempotency_key'] = str(uuid.uuid4())
        request.session['line_items'] = [line_item(f"Class on None student id: 1", 1, 5), ]

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
        context = {'paydict': paydict, 'rows': rows, 'total': total, 'bypass': bypass}
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
        sq_token = request.session.get('sq_token', None)

        if idempotency_key is None or sq_token is None:
            return render(request, 'student_app/message.html', {'message': 'payment processing error'})

        # Create an instance of the API Client
        # and initialize it with the credentials
        # for the Square account whose assets you want to manage

        client = Client(
            access_token=settings.SQUARE_CONFIG['access_token'],
            environment=settings.SQUARE_CONFIG['environment'],
        )

        # get the amount form the line items
        # also get line item name and add to notes
        amt = 0
        note = ""
        for line in request.session['line_items']:
            amt += line['base_price_money']['amount'] * int(line['quantity'])
            note += f" {line['name']},"

        # Monetary amounts are specified in the smallest unit of the applicable currency.
        amount = {'amount': amt, 'currency': 'USD'}

        result = client.payments.create_payment(
            body={
                "source_id": sq_token,
                "idempotency_key": idempotency_key,
                "amount_money": amount,
                "autocomplete": True,
                "location_id": settings.SQUARE_CONFIG['location_id'],
                "note": note
            }
        )

        if result.is_success():
            logging.debug(result.body)
        elif result.is_error():
            logging.debug(result.errors)

        # if not settings.DEBUG and not settings.TESTING:
        #     nonce = request.POST.get('nonce')

        #     # environment = square_cfg['environment']
        #     square_response = self.nonce(idempotency_key, nonce, request.session['line_items'])
        #     if isinstance(square_response, str):
        #         return render(request, 'student_app/message.html', {'message': 'payment processing error'})
        #     # if response.is_error():
        #     logging.debug(f"response type = {type(square_response)} response = {square_response}")
        # else:
        #     square_response = {'created_at': date.today().isoformat(), 'id': "", 'order_id': '', 'location_id': '',
        #                        'status': '', 'amount_money': {'amount': '12300'}, 'receipt_url': ''}

        # if request.session['payment_db'] == 'ClassRegistration':
        #     class_registration = ClassRegistration.objects.filter(idempotency_key=idempotency_key)
        #     for student in class_registration:
        #         student.pay_status = 'paid'
        #
        # description = request.session['line_items'][0]['name']
        # cd = date.fromisoformat(square_response['created_at'])
        # log = PaymentLog.objects.create(user=request.user,
        #                                 student_family=StudentFamily.objects.filter(user=request.user)[0],
        #                                 checkout_created_time=cd,
        #                                 checkout_id=square_response['id'],
        #                                 order_id=square_response['order_id'],
        #                                 location_id=square_response['location_id'],
        #                                 state=square_response['status'],
        #                                 total_money=square_response['amount_money']['amount'],
        #                                 description=description,
        #                                 idempotency_key=idempotency_key,
        #                                 receipt=square_response['receipt_url'])

        return render(request, 'student_app/message.html', {'message': 'payment successful'})
