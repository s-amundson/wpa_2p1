

def line_item(name, quantity, amount):
    # square requires amount in pennies
    l = {'name': name,
         'quantity': str(quantity),
         'base_price_money': {'amount': amount * quantity * 100,
                              'currency': 'USD'},
         }
    return l
