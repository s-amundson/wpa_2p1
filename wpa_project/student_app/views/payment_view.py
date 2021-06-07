import logging

from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from square.client import Client
from ..serializers import PaymentSerializer
from ..src.square_helper import log_response

logger = logging.getLogger(__name__)


class PaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        response_dict = {'status': 'ERROR', 'receipt_url': '', 'error': ''}
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            logging.debug(serializer.data)
            idempotency_key = request.session.get('idempotency_key', None)
            if idempotency_key is None:
                logging.debug('missing idempotency_key.')
                response_dict['error'] = 'payment processing error'
                return Response(response_dict)
            sq_token = serializer.data['sq_token']
            logging.debug(f'uuid = {idempotency_key}, sq_token = {sq_token}')

            if request.session.get('line_items', None) is None:
                response_dict['error'] = 'missing line items.'
                return Response(response_dict)

            # get the amount form the line items and get line item name and add to notes
            amt = 0
            note = ""
            for line in request.session['line_items']:
                amt += line['base_price_money']['amount'] * int(line['quantity'])
                note += f" {line['name']},"

            # Monetary amounts are specified in the smallest unit of the applicable currency.
            amount = {'amount': amt, 'currency': 'USD'}
            message = ""

            square_response = self.process_payment(idempotency_key, sq_token, note, amount)
            logging.debug(square_response['error'])
            if len(square_response['error']) > 0:
                for e in square_response['error']:
                    if e['code'] == 'GENERIC_DECLINE':
                        message += 'Card was declined, '
                    elif e['code'] == 'CVV_FAILURE':
                        message += 'Error with CVV, '
                    elif e['code'] == 'INVALID_EXPIRATION':
                        message += 'Invalid expiration date, '
                    else:
                        message += 'Other payment error'
                logging.debug(message)
                response_dict['error'] = message
                return Response(response_dict)
                # return redirect('registration:process_payment')
            log_response(request, square_response, create_date=None)

            response_dict = {'status': square_response['status'], 'receipt_url': square_response['receipt_url'],
                             'error': square_response['error']}
            return Response(response_dict)
        else:
            logging.debug(serializer.errors)
            response_dict['error'] = 'payment processing error'
            return JsonResponse(response_dict)

    def process_payment(self, idempotency_key, sq_token, note, amount):

        # Create an instance of the API Client
        # and initialize it with the credentials
        # for the Square account whose assets you want to manage

        client = Client(
            access_token=settings.SQUARE_CONFIG['access_token'],
            environment=settings.SQUARE_CONFIG['environment'],
        )

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
        square_response = result.body.get('payment', {'payment': None})
        if result.is_success():
            logging.debug(result.body)
            square_response['error'] = []
        elif result.is_error():
            logging.debug(result.errors)
            square_response['error'] = result.errors

        return square_response
