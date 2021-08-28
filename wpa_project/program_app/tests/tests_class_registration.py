import logging
import json
import time
import uuid

from django.test import TestCase, Client
from django.urls import reverse

from ..src import ClassRegistrationHelper
from ..models import BeginnerClass, ClassRegistration
from student_app.models import Student, StudentFamily, User

logger = logging.getLogger(__name__)


class TestsClassRegistration(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_class_get(self):
        response = self.client.get(reverse('programs:class_registration'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'program_app/class_registration.html')

    def test_class_register_good(self):
        # add a user to the class<option value="2022-06-05 09:00:00+00:00">05 Jun, 2022 09 AM / 11 AM</option>
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '1', 'student_1': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertEqual(cr[0].beginner_class, bc)
        self.assertEqual(self.client.session['line_items'][0]['name'],
                         'Class on 2022-06-05 student id: 1')
        self.assertEqual(self.client.session['payment_db'][1], 'ClassRegistration')

    def test_class_register_with_error(self):
        # Get the page
        # self.client.force_login(self.test_user)

        response = self.client.get(reverse('programs:class_registration'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'program_app/class_registration.html')

        # add a user to the class with error
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '2022-06 ', 'student_1': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 0)

    def test_class_register_over_limit(self):
        # put a record in to the database
        cr = ClassRegistration(beginner_class=BeginnerClass.objects.get(pk=1),
                               student=Student.objects.get(pk=1),
                               new_student=True,
                               pay_status='paid',
                               idempotency_key=str(uuid.uuid4()))
        cr.save()

        # change user, then try to add 2 more beginner students. Since limit is 2 can't add.
        self.client.force_login(User.objects.get(pk=2))
        self.client.post(reverse('programs:class_registration'),
                     {'beginner_class': '1', 'student_2': 'on', 'student_3': 'on', 'terms': 'on'}, secure=True)
        time.sleep(1)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 1)

    def test_class_register_readd(self):
        # put a record in to the database
        cr = ClassRegistration(beginner_class=BeginnerClass.objects.get(pk=1),
                               student=Student.objects.get(pk=1),
                               new_student=True,
                               pay_status='paid',
                               idempotency_key=str(uuid.uuid4()))
        cr.save()

        # try to add first user to class again.
        logging.debug('add user again')
        self.client.force_login(User.objects.get(pk=1))
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '1', 'student_1': 'on', 'terms': 'on'}, secure=True)
        time.sleep(1)
        # self.assertContains(response, 'Student already enrolled')
        # self.assertEqual(response.context['message'] == "")
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 1)

    def test_class_register_add2(self):
        # put a record in to the database
        cr = ClassRegistration(beginner_class=BeginnerClass.objects.get(pk=1),
                               student=Student.objects.get(pk=1),
                               new_student=True,
                               pay_status='paid',
                               idempotency_key=str(uuid.uuid4()))
        cr.save()

        # change user, then add 1 beginner students and 1 returnee.
        self.client.force_login(User.objects.get(pk=3))
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '1', 'student_4': 'on', 'student_5': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(pk=1)

        self.assertEqual(bc.state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 3)
        for c in cr:
            c.pay_status = 'paid'
            c.save()
        # don't change user, try to add user not in family to class
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '1', 'student_6': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        # self.assertEqual(bc.enrolled_beginners, 2)
        # self.assertEqual(bc.enrolled_returnee, 1)
        self.assertEqual(bc.state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 3)

        # change user, then add 1 returnee.
        self.client.force_login(User.objects.get(pk=4))
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '1', 'student_6': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.all()
        # self.assertEqual(bc[0].enrolled_beginners, 2)
        # self.assertEqual(bc[0].enrolled_returnee, 2)
        # self.assertEqual(bc[0].state, 'full')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 4)

    def test_no_pay_if_cost_zero(self):
        """test that no payment is required if the cost is set to 0"""
        # change the cost of the class
        bc = BeginnerClass.objects.get(pk=1)
        bc.cost = 0
        bc.save()
        # add a user to the class
        response = self.client.post(reverse('programs:class_registration'),
                                    {'beginner_class': '1', 'student_1': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertEqual(cr[0].beginner_class, bc)

        self.assertEqual(self.client.session['line_items'][0]['name'],
                         'Class on 2022-06-05 student id: 1')
        self.assertEqual(self.client.session['line_items'][0]['base_price_money']['amount'], 0)
        self.assertEqual(self.client.session['payment_db'][1], 'ClassRegistration')
        # self.assertTemplateUsed(response, 'student_app/message.html')

    def test_underage_student(self):
        sf = StudentFamily.objects.get(user=1)
        s = Student(student_family=sf,
                    first_name='Brad',
                    last_name='Conlan',
                    dob='2014-06-30')
        s.save()
        logging.debug(s)
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '1', 'student_1': 'on', f'student_{s.id}': 'on',
                          'terms': 'on'}, secure=True)
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 0)

    def test_check_space_full(self):
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '1', 'student_1': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(id=1)
        enrolled = ClassRegistrationHelper().enrolled_count(bc)
        logging.debug(enrolled)

        d = {'beginner_class': 1, 'beginner': 2, 'returnee': 2}
        self.assertTrue(ClassRegistrationHelper().check_space(d))
        bc = BeginnerClass.objects.get(id=1)
        self.assertEqual(bc.state, 'open')

        self.assertTrue(ClassRegistrationHelper().check_space(d, True))
        bc = BeginnerClass.objects.get(id=1)
        self.assertEqual(bc.state, 'full')

    def test_get_no_student(self):
        sf = StudentFamily.objects.get(pk=1)
        sf.delete()

        response = self.client.get(reverse('programs:class_registration'), secure=True)
        self.assertEqual(self.client.session['message'], 'Address form is required')
        # self.assertTemplateUsed(response, 'student_app/class_registration.html')

        response = self.client.get(reverse('programs:class_registered_table'), secure=True)
        self.assertEqual(self.client.session['message'], 'Address form is required')

    def test_class_register_return_for_payment(self):
        # add 1 beginner students and 1 returnee.
        self.client.force_login(User.objects.get(pk=3))
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '1', 'student_4': 'on', 'student_5': 'on', 'terms': 'on'}, secure=True)

        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)
        response = self.client.get(reverse('programs:class_registration', kwargs={'reg_id': 1}), secure=True)
        self.assertEqual(self.client.session['payment_db'][1], 'ClassRegistration')
        self.assertEqual(self.client.session['idempotency_key'], str(cr[0].idempotency_key))

    def test_class_status(self):
        # add 1 beginner students and 1 returnee.
        self.client.force_login(User.objects.get(pk=3))
        # response = self.client.get(reverse('programs:class_status', kwargs={'class_date': '2022-06-05'}), secure=True)
        response = self.client.get(reverse('programs:class_status', kwargs={'class_id': '1'}), secure=True)
        content = json.loads(response.content)
        self.assertEqual(content['status'], 'open')
        self.assertEqual(content['beginner'], 2)
        self.assertEqual(content['returnee'], 2)

        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '1', 'student_4': 'on', 'student_5': 'on', 'terms': 'on'}, secure=True)
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)
        for c in cr:
            c.pay_status = 'paid'
            c.save()

        # response = self.client.get(reverse('programs:class_status', kwargs={'class_date': '2022-06-05'}), secure=True)
        response = self.client.get(reverse('programs:class_status', kwargs={'class_id': '1'}), secure=True)
        content = json.loads(response.content)
        self.assertEqual(content['status'], 'open')
        self.assertEqual(content['beginner'], 1)
        self.assertEqual(content['returnee'], 1)

    def test_get_class_registered_table(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('programs:class_registered_table'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'program_app/tables/class_registered_table.html')
