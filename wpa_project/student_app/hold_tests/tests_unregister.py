import json
import logging
import time

from django.test import TestCase, Client
from django.urls import reverse
from ..models import BeginnerClass, ClassRegistration, PaymentLog, RefundLog, Student, User

logger = logging.getLogger(__name__)


class TestsUnregisterStudent(TestCase):
    fixtures = ['f1']  # , 'f2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def eval_content(self, content, status, error, length):
        logging.debug(content)
        self.assertEqual(content['status'], status)
        self.assertEqual(content['error'], error)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), length)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        # session = self.client.session
        # session['idempotency_key'] = str(uuid.uuid4())
        # session['line_items'] = [{'name': 'Class on None student id: 1',
        #                           'quantity': '1', 'base_price_money': {'amount': 500, 'currency': 'USD'}}]
        # logging.debug(session['line_items'])
        # session.save()

    # def test_refund_success_entire_purchase(self):
    #     self.client.post(reverse('registration:class_registration'),
    #                      {'beginner_class': '2022-06-05', 'student_2': 'on', 'student_3': 'on'}, secure=True)
    #     bc = BeginnerClass.objects.all()
    #     logging.debug(bc.values())
    #     self.assertEqual(bc[0].enrolled_beginners, 2)
    #     self.assertEqual(bc[0].enrolled_returnee, 0)
    #     self.assertEqual(bc[0].state, 'open')
    #     cr = ClassRegistration.objects.all()
    #     self.assertEqual(len(cr), 2)
    #
    #     # process a good payment
    #     response = self.client.post(reverse('registration:payment'),
    #                                 {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
    #     self.eval_content(json.loads(response.content), 'COMPLETED', [], 1)
    #     cr = ClassRegistration.objects.all()
    #     self.assertEqual(len(cr), 2)
    #     logging.debug(cr[0].pay_status)
    #
    #     # give square some time to process the payment got bad requests without it.
    #     time.sleep(5)
    #
    #     # make student a returnee and the class full
    #     student = Student.objects.get(pk=3)
    #     student.safety_class = '2020-01-01'
    #     student.save()
    #     bc = BeginnerClass.objects.get(pk=1)
    #     bc.enrolled_returnee = 2
    #     bc.state = 'full'
    #     bc.save()
    #
    #     response = self.client.post(reverse('registration:unregister_class'),
    #                                 {'class_list': ['1', '2']}, secure=True)
    #     logging.debug(response.data)
    #     self.assertEqual(response.data['status'], 'SUCCESS')
    #     rl = RefundLog.objects.all()
    #     self.assertEqual(len(rl), 1)
    #     self.assertEqual(rl[0].amount, 1000)
    #     pl = PaymentLog.objects.filter(payment_id=rl[0].payment_id)
    #     self.assertEqual(len(pl), 1)
    #     self.assertEqual(pl[0].status, 'refund')
    #     bc = BeginnerClass.objects.get(pk=1)
    #     # logging.debug(bc.values())
    #     self.assertEqual(bc.enrolled_beginners, 1)
    #     self.assertEqual(bc.enrolled_returnee, 1)
    #     self.assertEqual(bc.state, 'open')
    #     # cr = ClassRegistration.objects.get(beginner_class=bc)
    #     cr = bc.classregistration_set.all()
    #     logging.debug(len(cr))
    #     self.assertEqual(cr[0].pay_status, 'refunded')
    #     self.assertEqual(cr[1].pay_status, 'refunded')
    #
    def test_refund_success_partial_purchase(self):
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': '2022-06-05', 'student_2': 'on', 'student_3': 'on'}, secure=True)

        # process a good payment
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'COMPLETED', [], 1)
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)
        logging.debug(cr[0].pay_status)
        time.sleep(5)

        response = self.client.post(reverse('registration:unregister_class'),
                                    {'class_list': ['2']}, secure=True)
        logging.debug(response.data)
        self.assertEqual(response.data['status'], 'SUCCESS')
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(rl[0].amount, 500)
        pl = PaymentLog.objects.filter(payment_id=rl[0].payment_id)
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].status, 'refund')

    # def test_refund_invalid_student(self):
    #
    #     self.test_user = User.objects.get(pk=3)
    #     self.client.force_login(self.test_user)
    #     response = self.client.post(reverse('registration:unregister_class'),
    #                                 {'class_list': ['1', '2']}, secure=True)
    #     logging.debug(response.data)
    #     self.assertEqual(response.data['status'], 'ERROR')

    # def test_refund_class_wrong(self):
    #     bc = BeginnerClass.objects.get(pk=1)
    #     for state in ['closed', 'canceled', 'recorded']:
    #         bc.state = state
    #         bc.save()
    #         response = self.client.post(reverse('registration:unregister_class'),
    #                                     {'class_list': ['1', '2']}, secure=True)
    #         logging.debug(response.data)
    #         self.assertEqual(response.data['status'], 'ERROR')
# {'refund':
#   {'amount_money': {'amount': 5, 'currency': 'USD'},
#   'created_at': '2021-06-08T22:57:56.361Z',
#   'id': 'hGlJwNfQxPQ5FjohtPrud7lKqpYZY_59WvXVSTGo3dcZKNNmkv5GMHeBcVuAPhKZiGmPsoNsM',
#   'location_id': 'SVM1F73THA9W6',
#   'order_id': '5NSwgFUNiBio3ksoL0iVgDFsCi4F',
#   'payment_id': 'hGlJwNfQxPQ5FjohtPrud7lKqpYZY',
#   'status': 'PENDING',
#   'updated_at': '2021-06-08T22:57:56.361Z'}}