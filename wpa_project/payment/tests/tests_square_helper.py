# import logging
# import time
# import uuid
# from datetime import datetime
#
# from django.test import TestCase, Client
# from django.urls import reverse
# from django.apps import apps
#
# from student_app.models import Student
# from ..models import PaymentLog, RefundLog
# from ..src import SquareHelper
#
# logger = logging.getLogger(__name__)
#
#
# class TestsSquareHelper(TestCase):
#     fixtures = ['f1']
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.User = apps.get_model(app_label='student_app', model_name='User')
#
#     def setUp(self):
#         # Every test needs a client.
#         self.client = Client()
#         self.test_user = self.User.objects.get(pk=2)
#         self.client.force_login(self.test_user)
#         session = self.client.session
#         session['idempotency_key'] = str(uuid.uuid4())
#         session['line_items'] = [{'name': 'Class on None student id: 1',
#                                   'quantity': '1', 'base_price_money': {'amount': 500, 'currency': 'USD'}}]
#         session.save()
#
#     def test_refund_bypass(self):
#         response = self.client.post(reverse('payment:process_payment'),
#                                     {'bypass': ''}, secure=True)
#         self.assertTemplateUsed('student_app/message.html')
#         pl = PaymentLog.objects.all()
#         self.assertEqual(len(pl), 1)
#         logging.debug(pl[0].id)
#
#         sh = SquareHelper()
#         rp = sh.refund_payment(pl[0].idempotency_key, 500)
#         pl = PaymentLog.objects.get(pk=pl[0].id)
#         self.assertEqual(pl.status, 'refund')
#         self.assertEqual(rp, {'status': "SUCCESS", 'error': ''})
#         logging.debug(pl.total_money)
#
#         rp = sh.refund_payment(pl.idempotency_key, 500)
#         logging.debug(rp)
#         # self.assertEqual(rp['error'][0]['code'], 'VALUE_EMPTY')
#         self.assertIsNone(rp['refund'])
#
#         pl.total_money = 0
#         pl.save()
#         rp = sh.refund_payment(pl.idempotency_key, 500)
#         self.assertEqual(rp, {'status': 'error', 'error': 'Previously refunded'})
#
#     def test_square_helper_refund_payment_error(self):
#         rp = SquareHelper().refund_payment(str(uuid.uuid4()), 1000)
#         self.assertEqual(rp, {'status': "FAIL"})
#
#     def test_square_helper_refund_payment(self):
#
#         uid = str(uuid.uuid4())
#         sh = SquareHelper()
#         square_response = sh.process_payment(uid, 'cnon:card-nonce-ok', 'test payment', {'amount': 1000, 'currency': 'USD'})
#         logging.debug(square_response)
#         log = PaymentLog.objects.create(
#             user=self.test_user,
#             student_family=Student.objects.get(user=self.test_user).student_family,
#             checkout_created_time=datetime.strptime(square_response['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
#             db_model='test',
#             description=square_response['note'],
#             location_id=square_response['location_id'],
#             idempotency_key=uid,
#             order_id=square_response['order_id'],
#             payment_id=square_response['id'],
#             receipt=square_response['receipt_url'],
#             source_type=square_response['source_type'],
#             status=square_response['status'],
#             total_money=square_response['approved_money']['amount'],
#             )
#         log.save()
#         self.assertEqual(PaymentLog.objects.count(), 1)
#         # give square some time to process the payment got bad requests without it.
#         time.sleep(5)
#
#         logging.debug(sh.refund_payment(uid, 5))
#         self.assertEqual(RefundLog.objects.count(), 1)
#         time.sleep(5)
#
#         logging.debug(sh.refund_payment(uid, 1))
#         self.assertEqual(RefundLog.objects.count(), 2)
