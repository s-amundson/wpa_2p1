from django.utils import timezone
from ..models import Card, Customer, PaymentLog, RefundLog
from student_app.models import User


class MockSideEffects:
    """ Used for testing in other apps to mock payments. Faster processing"""
    def add_card(self, user):
        customer = Customer.objects.create(user=user,
                                           customer_id="9Z9Q0D09F0WMV0FHFA2QMZH8SC",
                                           created_at="2022-05-30T19:50:46Z",
                                           creation_source="THIRD_PARTY",
                                           updated_at="2022-05-30T19:50:46Z")
        card = Card.objects.create(
            bin=411111,
            card_brand="VISA",
            card_id="ccof:8sLQqf1boPfmwDKI4GB",
            card_type="CREDIT",
            cardholder_name="",
            customer=customer,
            default=1,
            enabled=1,
            exp_month=11,
            exp_year=2022,
            fingerprint="sq-1-npXvWJT5AhTtISQwBYohbA8kkQ24CyPCN6G6kP_6Bm_K2KPYsT1y_1xKUhvAnMIzfA",
            # id=1,
            last_4=1111,
            merchant_id="TYXMY2T8CN2PK",
            prepaid_type="NOT_PREPAID",
            version=0)
        return card

    def payment_side_effect(self, amount, category, donation, idempotency_key, note, source_id, autocomplete=True,
                            saved_card_id=0):
        response = {'created_at': timezone.now(),
                    'location_id': 'test_location',
                    'order_id': 'test_order',
                    'id': 'test_id',
                    'receipt_url': '',
                    'source_type': 'test',
                    'status': 'SUCCESS',
                    'approved_money': {'amount': amount * 100}
                    }
        payment = PaymentLog.objects.create(
            category=category,
            checkout_created_time=response['created_at'],
            description=note[:250],  # database set to 255 characters
            donation=donation * 100,  # storing pennies in the database
            idempotency_key=idempotency_key,
            location_id=response['location_id'],
            order_id=response['order_id'],
            payment_id=response['id'],
            receipt=response['receipt_url'],
            source_type=response['source_type'],
            status=response['status'],
            total_money=response['approved_money']['amount'],
            user=User.objects.get(pk=3)
        )
        return payment

    def refund_side_effect(self, log, amount):
        log.status = 'refund'
        log.save()
        RefundLog.objects.create(amount=amount,
                                 created_time=timezone.now(),
                                 location_id='',
                                 order_id='',
                                 payment_id='test_payment',
                                 processing_fee=None,
                                 refund_id='test_refund',
                                 status='SUCCESS'
                                 )
        return {
            'status': "SUCCESS",
            'created_at': timezone.now(),
            'error': '',
            'location_id': 'test_location',
            'order_id': 'test_order',
            'payment_id': 'log.payment_id',
            'id': 'test_refund',
            'amount_money': {'amount': amount}
            }
