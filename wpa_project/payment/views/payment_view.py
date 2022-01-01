import logging

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from ..serializers import PaymentSerializer
from ..src import SquareHelper, EmailMessage

logger = logging.getLogger(__name__)


class PaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self):
        self.square_helper = SquareHelper()

    def post(self, request, format=None):
        response_dict = {'status': 'ERROR', 'receipt_url': '', 'error': '', 'continue': False}
        serializer = PaymentSerializer(data=request.data)
        logging.debug(request.data)
        if serializer.is_valid():
            idempotency_key = request.session.get('idempotency_key', None)
            if idempotency_key is None:
                logging.debug('missing idempotency_key.')
                response_dict['error'] = 'payment processing error'
                return Response(response_dict)
            sq_token = serializer.data['sq_token']

            if request.session.get('line_items', None) is None:
                response_dict['error'] = 'missing line items.'
                return Response(response_dict)

            # if user donated money add it to the line itmes.
            donation = serializer.data.get('donation', None)
            if donation is not None:
                request.session['line_items'].append(self.square_helper.line_item('donation', 1, float(donation)))

            # get the amount form the line items and get line item name and add to notes
            amt = 0
            note = ""
            for line in request.session['line_items']:
                amt += line['base_price_money']['amount'] * int(line['quantity'])
                note += f" {line['name']},"

            # Monetary amounts are specified in the smallest unit of the applicable currency.
            amount = {'amount': amt, 'currency': 'USD'}
            message = ""
            logging.debug(amt)
            if amt == 0:
                square_response = self.square_helper.comp_response(note, amt)
            elif sq_token == 'bypass' and request.user.is_board:
                square_response = self.square_helper.comp_response(note, amt)
            else:
                square_response = self.square_helper.process_payment(idempotency_key, sq_token, note, amount)
                logging.debug(square_response)
                if len(square_response['error']) > 0:
                    for e in square_response['error']:
                        if e['code'] == 'GENERIC_DECLINE':
                            message += 'Card was declined, '
                        elif e['code'] == 'CVV_FAILURE':
                            message += 'Error with CVV, '
                        elif e['code'] == 'INVALID_EXPIRATION':
                            message += 'Invalid expiration date, '
                        elif e['code'] == 'ADDRESS_VERIFICATION_FAILURE':  # pragma: no cover
                            message += 'Invalid zip code, '
                        else:  # pragma: no cover
                            message += 'Other payment error'
                    # logging.debug(message)
                    response_dict['error'] = message
                    response_dict['continue'] = self.square_helper.payment_error(request)
                    return Response(response_dict)
                # return redirect('registration:process_payment')
            self.square_helper.log_payment(request, square_response, create_date=None)
            logging.debug(self.request.session.get("account_verified_email"))
            pay_dict = {'line_items': request.session['line_items'], 'total': amt / 100,
                        'receipt': square_response['receipt_url']}
            EmailMessage().payment_email_user(request.user, pay_dict)
            response_dict = {'status': square_response['status'], 'receipt_url': square_response['receipt_url'],
                             'error': square_response['error'], 'continue': False}
            return Response(response_dict)
        else:
            logging.debug(serializer.errors)
            response_dict['error'] = 'payment processing error'
            return JsonResponse(response_dict)
