import logging
from datetime import timedelta
from django.conf import settings
from django.shortcuts import render
from django.utils.datetime_safe import date
from django.views.generic.base import View

from ..models import ClassRegistration, PaymentLog, StudentFamily

#
# from registration.models import Joad_session_registration, Member, Payment_log, Membership
# from registration.src.Email import Email

logger = logging.getLogger(__name__)


class ProcessPaymentView(View):
    """Shows a payment page for making purchases"""

    def get(self, request):
        paydict = {}
        if settings.SQUARE_CONFIG['environment'] == "production":
            # paydict['production'] = True
            paydict['pay_url'] = "https://js.squareup.com/v2/paymentform"
        else:
            # paydict['production'] = False
            paydict['pay_url'] = "https://js.squareupsandbox.com/v2/paymentform"
        paydict['app_id'] = settings.SQUARE_CONFIG['application_id']
        paydict['location_id'] = settings.SQUARE_CONFIG['location_id']
        rows, total = self.table_rows(request.session)
        bypass = False
        if settings.DEBUG or request.user.is_authenticated:
            bypass = True
        logging.debug(paydict)
        context = {'paydict': paydict, 'rows': rows, 'total': total, 'bypass': bypass}
        return render(request, 'student_app/square_pay.html', context)

    def nonce(self, idempotency_key, nonce, line_items):
        """Process payment with squares nonce"""
        # Every payment you process with the SDK must have a unique idempotency key.
        # If you're unsure whether a particular payment succeeded, you can reattempt
        # it with the same idempotency key without worrying about double charging
        # the buyer.
        # idempotency_key = str(uuid.uuid1())

        # get the amount form the line items
        # also get line item name and add to notes
        amt = 0
        note = ""
        for line in line_items:
            amt += line['base_price_money']['amount'] * int(line['quantity'])
            note += f" {line['name']},"

        # Monetary amounts are specified in the smallest unit of the applicable currency.
        amount = {'amount': amt, 'currency': 'USD'}

        # To learn more about splitting payments with additional recipients,
        # see the Payments API documentation on our [developer site]
        # (https://developer.squareup.com/docs/payments-api/overview).
        body = {'idempotency_key': idempotency_key, 'source_id': nonce, 'amount_money': amount}

        # not sure if line items belongs in nonce
        body['order'] = {}
        body['order']['reference_id'] = idempotency_key
        body['order']['line_items'] = line_items
        body['note'] = note

        # The SDK throws an exception if a Connect endpoint responds with anything besides
        # a 200-level HTTP code. This block catches any exceptions that occur from the request.
        api_response = self.client.payments.create_payment(body)
        if api_response.is_success():
            res = api_response.body['payment']
        elif api_response.is_error():
            res = "Exception when calling PaymentsApi->create_payment: {}".format(api_response.errors)

        return res

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
        idempotency_key = request.session.get('idempotency_key', None)

        if idempotency_key is None:
            return render(request, 'registration/message.html', {'message': 'payment processing error'})

        if not settings.DEBUG and not settings.TESTING:
            nonce = request.POST.get('nonce')

            # environment = square_cfg['environment']
            square_response = self.nonce(idempotency_key, nonce, request.session['line_items'])
            if isinstance(square_response, str):
                return render(request, 'registration/message.html', {'message': 'payment processing error'})
            # if response.is_error():
            logging.debug(f"response type = {type(square_response)} response = {square_response}")
        else:
            square_response = {'created_at': date.today().isoformat(), 'id': "", 'order_id': '', 'location_id': '',
                               'status': '', 'amount_money': {'amount': '12300'}, 'receipt_url': ''}

        if request.session['payment_db'] == 'ClassRegistration':
            class_registration = ClassRegistration.objects.filter(idempotency_key=idempotency_key)
            for student in class_registration:
                student.pay_status = 'paid'

        description = request.session['line_items'][0]['name']
        cd = date.fromisoformat(square_response['created_at'])
        log = PaymentLog.objects.create(user=request.user,
                                        student_family=StudentFamily.objects.filter(user=request.user)[0],
                                        checkout_created_time=cd,
                                        checkout_id=square_response['id'],
                                        order_id=square_response['order_id'],
                                        location_id=square_response['location_id'],
                                        state=square_response['status'],
                                        total_money=square_response['amount_money']['amount'],
                                        description=description,
                                        idempotency_key=idempotency_key,
                                        receipt=square_response['receipt_url'])

        return render(request, 'student_app/message.html', {'message': 'payment successful'})
