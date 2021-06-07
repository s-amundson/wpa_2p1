from django.apps import apps
from django.utils.datetime_safe import datetime
from ..models import PaymentLog, StudentFamily

def line_item(name, quantity, amount):
    # square requires amount in pennies
    l = {'name': name,
         'quantity': str(quantity),
         'base_price_money': {'amount': amount * quantity * 100,
                              'currency': 'USD'},
         }
    return l


def dummy_response(note, amount):
    body = {
        'payment': {'approved_money': amount,
                    'created_at': '2021-06-06T00:24:48.978Z',
                    'id': None,
                    'location_id': 'SVM1F73THA9W6',
                    'note': note,
                    'order_id': None,
                    'receipt_url': None,
                    'source_type': None,
                    'status': 'comped',
                    'total_money': amount}}
    return body['payment']


def log_response(request, square_response, create_date=None):
    if create_date is None:
        create_date = datetime.strptime(square_response['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    log = PaymentLog.objects.create(user=request.user,
                                    student_family=StudentFamily.objects.filter(user=request.user)[0],
                                    checkout_created_time=create_date,
                                    checkout_id=square_response['id'],
                                    db_model=request.session.get('payment_db', None),
                                    description=square_response['note'],
                                    location_id=square_response['location_id'],
                                    idempotency_key=request.session['idempotency_key'],
                                    order_id=square_response['order_id'],
                                    receipt=square_response['receipt_url'],
                                    source_type=square_response['source_type'],
                                    state=square_response['status'],
                                    total_money=square_response['approved_money']['amount'],
                                    )
    # TODO email receipt if exists

    if request.session.get('payment_db', None) is not None:
        m = apps.get_model(app_label='student_app', model_name=request.session['payment_db'])
        records = m.objects.filter(idempotency_key=request.session['idempotency_key'])
        for record in records:
            record.pay_status = 'paid'
            record.save()
