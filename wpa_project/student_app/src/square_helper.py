
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
