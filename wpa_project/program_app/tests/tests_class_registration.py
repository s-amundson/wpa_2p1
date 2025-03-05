import datetime
import logging
import uuid
from unittest.mock import patch

from django.test import TestCase, Client, tag
from django.urls import reverse
from django.utils import timezone

from ..models import BeginnerClass
from event.models import Event, Registration
from student_app.models import Student, StudentFamily, User
from payment.models import Card, Customer

logger = logging.getLogger(__name__)


class TestsClassRegistration(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            id=1,
            last_4=1111,
            merchant_id="TYXMY2T8CN2PK",
            prepaid_type="NOT_PREPAID",
            version=0)
        return card

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        self.event = Event.objects.get(pk=1)
        self.event.event_date = (timezone.now() + timezone.timedelta(days=5)).replace(hour=9, minute=0, second=0)
        self.event.save()

    def get_post_dict(self, events):
        self.post_dict = {
            'event': events,
            'terms': True,
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-register': True,
            'form-0-student': 4,
            'form-1-register': False,
            'form-1-student': 5,
            }
        return self.post_dict

    def test_class_get(self):
        response = self.client.get(reverse('programs:class_registration'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'program_app/class_registration.html')

    def test_class_get_no_auth(self):
        self.client.logout()
        response = self.client.get(reverse('programs:class_registration'), secure=True)
        self.assertEqual(response.status_code, 302)

    def test_class_get_no_student(self):
        student = self.test_user.student_set.first()
        student.user = None
        student.save()

        response = self.client.get(reverse('programs:class_registration'), secure=True)
        self.assertRedirects(response, reverse('registration:profile'))

    def test_class_get_no_student_family(self):
        student = self.test_user.student_set.first()
        student.student_family = None
        student.save()

        response = self.client.get(reverse('programs:class_registration'), secure=True)
        self.assertRedirects(response, reverse('registration:profile'))

    # @tag('temp')
    def test_class_register_good(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.save()

        # add a user to the class
        response = self.client.post(reverse('programs:class_registration'),
                         self.get_post_dict([self.event.id]), secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertEqual(cr[0].event, bc.event)
        self.assertEqual(self.client.session['line_items'][0]['name'],
                         f'Class on {str(self.event.event_date)[:10]} student: Charles')
        self.assertEqual(self.client.session['payment_category'], 'intro')
        self.assertTrue(self.client.session['instructions'].startswith(
                            'Please plan to be at the range 30 minutes prior to the class to allow us to sign you in.'))
        self.assertEqual(cr[0].user, self.test_user)

    def test_class_register_over_limit(self):
        # put a record in to the database
        cr = Registration(
            event=self.event,
            student=Student.objects.get(pk=4),
            pay_status='paid',
            idempotency_key=str(uuid.uuid4()))
        cr.save()
        u = User.objects.get(pk=2)
        u.is_staff = False
        u.save()

        # change user, then try to add 2 more beginner students. Since limit is 2 can't add.
        self.client.force_login(u)
        self.get_post_dict([self.event.id])
        self.post_dict['form-0-student'] = 2
        self.post_dict['form-1-student'] = 3
        self.post_dict['form-1-register'] = True
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)

        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertContains(response, 'Not enough space available in this class')

    def test_class_register_readd(self):
        # put a record in to the database
        cr = Registration(
            event=self.event,
            student=Student.objects.get(pk=4),
            pay_status='paid',
            idempotency_key=str(uuid.uuid4()))
        cr.save()

        # try to add first user to class again.
        self.get_post_dict([self.event.id])
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)
        self.assertContains(response, 'Student is already enrolled')
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)

    def test_class_register_readd_staff(self):
        # put a record in to the database
        cr = Registration(
            event=self.event,
            student=Student.objects.get(pk=2),
            pay_status='paid',
            idempotency_key=str(uuid.uuid4()))
        cr.save()
        # try to add first user to class again.
        self.client.force_login(User.objects.get(pk=2))
        self.get_post_dict([self.event.id])
        self.post_dict['form-0-student'] = 2
        self.post_dict['form-1-student'] = 3
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)
        self.assertContains(response, 'Student is already enrolled')

        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)

    def test_class_register_add2(self):
        # put a record in to the database
        cr = Registration(
            event=self.event,
            student=Student.objects.get(pk=1),
            pay_status='paid',
            idempotency_key=str(uuid.uuid4()))
        cr.save()

        # change user, then add 1 beginner students and 1 returnee.
        self.get_post_dict([self.event.id])
        self.post_dict['form-1-register'] = True
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)
        bc = BeginnerClass.objects.get(pk=1)

        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 3)
        for c in cr:
            c.pay_status = 'paid'
            c.save()
        # don't change user, try to add user not in family to class
        self.post_dict.pop('form-1-register')
        self.post_dict.pop('form-1-student')
        # self.post_dict.pop('form-1-event')

        logger.warning(self.post_dict)
        self.post_dict['form-0-student'] = 6
        self.post_dict['form-TOTAL_FORMS'] = 1
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)

        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 3)

        # change user, then add 1 returnee.
        self.client.force_login(User.objects.get(pk=5))
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)

        cr = Registration.objects.all()
        self.assertEqual(len(cr), 4)

    def test_no_pay_if_cost_zero(self):
        """test that no payment is required if the cost is set to 0"""

        # change the cost of the class
        # event = Event.objects.get(pk=1)
        self.event.cost_standard = 0
        self.event.save()

        # add a user to the class
        response = self.client.post(reverse('programs:class_registration'), self.get_post_dict([self.event.id]), secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertEqual(cr[0].event, bc.event)

        self.assertEqual(self.client.session['line_items'][0]['name'],
                         f'Class on {str(self.event.event_date)[:10]} student: Charles')
        self.assertEqual(self.client.session['line_items'][0]['amount_each'], 0)
        self.assertEqual(self.client.session['payment_category'], 'intro')
        self.assertEqual(cr[0].user, self.test_user)

    # @tag('temp')
    def test_underage_student(self):
        sf = StudentFamily.objects.get(pk=3)
        d = timezone.now()
        d.replace(year=d.year - 7)
        s = Student(student_family=sf,
                    first_name='Brad',
                    last_name='Conlan',
                    dob=d.date())
        s.save()

        self.get_post_dict([self.event.id])
        self.post_dict['form-1-student'] = s.id
        self.post_dict['form-1-register'] = True

        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 0)
        self.assertContains(response, 'Student must be at least 9 years old to participate')

    def test_get_no_student(self):
        sf = StudentFamily.objects.get(pk=3)
        sf.delete()
        sf.save()

        response = self.client.get(reverse('programs:class_registration'), secure=True)
        self.assertEqual(self.client.session['message'], 'Address form is required')
        self.assertRedirects(response, reverse('registration:profile'))

    # @tag('temp')
    def test_class_register_return_for_payment(self):
        # add 1 beginner students and 1 returnee.

        self.get_post_dict([self.event.id])
        self.post_dict['form-1-register'] = True

        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)

        cr = Registration.objects.all()
        self.assertEqual(len(cr), 2)
        response = self.client.get(reverse('programs:resume_registration', kwargs={'reg_id': 1}), secure=True)
        self.assertEqual(self.client.session['idempotency_key'], str(cr[0].idempotency_key))
        self.assertEqual(self.client.session['payment_category'], 'intro')
        self.assertTrue(self.client.session['instructions'].startswith(
                            'Please plan to be at the range 15 minutes prior to the class to allow us to sign you in.'))

    def test_class_register_instructor_current(self):
        # make user instructor
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.test_user.is_instructor = True
        d = timezone.now()
        self.test_user.instructor_expire_date = d.replace(year=d.year + 1)
        self.test_user.save()

        # add a user to the class
        self.get_post_dict([self.event.id])
        self.post_dict['form-0-comment'] = 'flying kites today'
        self.post_dict.pop('form-1-register')
        self.post_dict.pop('form-1-student')

        self.post_dict['form-0-student'] = 1
        self.post_dict['form-TOTAL_FORMS'] = 1
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)

        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertEqual(cr[0].event, bc.event)
        self.assertEqual(cr[0].comment, 'flying kites today')
        self.assertEqual(self.client.session['line_items'][0]['name'],
                         f'Class on {str(self.event.event_date)[:10]} staff: Emily')
        self.assertEqual(cr[0].user, self.test_user)

    def test_class_register_instructor_current_multiple(self):
        # make user instructor
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.test_user.is_instructor = True
        d = timezone.now()
        self.test_user.instructor_expire_date = d.replace(year=d.year + 1)
        self.test_user.save()

        e2 = Event.objects.get(pk=2)
        e2.event_date = (timezone.now() + timezone.timedelta(days=5)).replace(hour=11, minute=0, second=0)
        e2.save()
        # add a user to the class
        self.get_post_dict([self.event.id, e2.id])
        self.post_dict['form-0-comment'] = 'flying kites today'
        self.post_dict.pop('form-1-register')
        self.post_dict.pop('form-1-student')

        self.post_dict['form-0-student'] = 1
        self.post_dict['form-TOTAL_FORMS'] = 1
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)

        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 2)
        self.assertEqual(cr[0].event, bc.event)
        self.assertEqual(cr[0].comment, 'flying kites today')
        self.assertEqual(self.client.session['line_items'][0]['name'],
                         f'Class on {str(self.event.event_date)[:10]} staff: Emily')
        self.assertEqual(cr[0].user, self.test_user)

    # def test_class_register_instructor_overdue(self):
    #     # make user instructor
    #     self.test_user = User.objects.get(pk=1)
    #     self.client.force_login(self.test_user)
    #     self.test_user.is_instructor = True
    #     d = timezone.now() - timezone.timedelta(days=30)
    #     self.test_user.instructor_expire_date = d
    #     self.test_user.save()
    #
    #     # add a user to the class
    #     self.get_post_dict([self.event.id])
    #     self.post_dict.pop('form-1-register')
    #     self.post_dict.pop('form-1-student')
    #
    #     self.post_dict['form-0-student'] = 1
    #     self.post_dict['form-TOTAL_FORMS'] = 1
    #     response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)
    #     bc = BeginnerClass.objects.get(pk=1)
    #     self.assertEqual(bc.event.state, 'open')
    #     cr = Registration.objects.all()
    #     self.assertEqual(len(cr), 0)

    @patch('program_app.src.class_registration_helper.ClassRegistrationHelper.update_class_state')
    def test_class_register_instructor_full(self, update_class_state):
        # Don't add an instructor when instructors are at limit.
        # use the patch so that we don't open the class back up.

        # make user instructor
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.test_user.is_instructor = True
        d = timezone.now()
        self.test_user.instructor_expire_date = d + timezone.timedelta(days=30)
        self.test_user.save()

        bc = BeginnerClass.objects.get(pk=1)
        bc.instructor_limit = 0
        bc.save()

        # add a user to the class
        self.get_post_dict([self.event.id])
        self.post_dict.pop('form-1-register')
        self.post_dict.pop('form-1-student')

        self.post_dict['form-0-student'] = 1
        self.post_dict['form-TOTAL_FORMS'] = 1
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 0)
        update_class_state.assert_called_with(bc)

    @patch('program_app.src.class_registration_helper.ClassRegistrationHelper.update_class_state')
    def test_class_register_instructor_full2(self, update_class_state):
        # Add instructor when the class is full of students but open instructor positions.
        # use the patch so that we don't open the class back up.
        # make user instructor
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.test_user.is_instructor = True
        d = timezone.now()
        self.test_user.instructor_expire_date = d + timezone.timedelta(days=30)
        self.test_user.save()

        # bc = BeginnerClass.objects.get(pk=1)
        self.event.state = 'full'
        self.event.save()

        # add a user to the class
        self.get_post_dict([self.event.id])
        self.post_dict.pop('form-1-register')
        self.post_dict.pop('form-1-student')

        self.post_dict['form-0-student'] = 1
        self.post_dict['form-TOTAL_FORMS'] = 1
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'full')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        update_class_state.assert_called_with(bc)

    @patch('program_app.src.class_registration_helper.ClassRegistrationHelper.update_class_state')
    def test_class_register_staff_full(self, update_class_state):
        # Add instructor when the class is full of students but open instructor positions.
        # use the patch so that we don't open the class back up.
        # make user instructor
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        d = timezone.now()

        self.event.state = 'full'
        self.event.save()

        # add a user to the class
        self.get_post_dict([self.event.id])
        self.post_dict.pop('form-1-register')
        self.post_dict.pop('form-1-student')

        self.post_dict['form-0-student'] = 2
        self.post_dict['form-TOTAL_FORMS'] = 1
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)

        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'full')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        update_class_state.assert_called_with(bc)

    def test_resume_registration_no_wait(self):
        cr = Registration(event=self.event,
                          student=Student.objects.get(pk=4),
                          pay_status='start',
                          idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
                          reg_time='2021-06-09',
                          attended=False)
        cr.save()
        response = self.client.get(reverse('programs:resume_registration', kwargs={'reg_id': cr.id}), secure=True)
        self.assertRedirects(response, reverse('payment:make_payment'))

    # @tag('temp')
    def test_resume_registration_no_wait_with_cancel(self):
        cr = Registration(event=self.event,
                          student=Student.objects.get(pk=4),
                          pay_status='start',
                          idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
                          reg_time='2021-06-09',
                          attended=False)
        cr.save()
        Registration.objects.create(
            event=self.event,
            student=Student.objects.get(pk=4),
            pay_status='canceled',
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)
        response = self.client.get(reverse('programs:resume_registration', kwargs={'reg_id': cr.id}), secure=True)
        self.assertRedirects(response, reverse('payment:make_payment'))
        self.assertEqual(len(self.client.session['line_items']), 1)
        logger.warning(self.client.session['line_items'])

    def test_new_student_register_twice(self):
        d = timezone.now() + datetime.timedelta(days=2)
        bc = BeginnerClass.objects.get(pk=1)
        bc.event.event_date = d
        bc.class_type = 'beginner'
        bc.event.save()
        bc.save()
        s = Student.objects.get(pk=4)
        cr = Registration(event=bc.event,
                          student=s,
                          pay_status='start',
                          idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
                          reg_time='2021-06-09',
                          attended=False)
        cr.save()

        bc2 = BeginnerClass.objects.get(pk=2)
        bc2.event.event_date = d + datetime.timedelta(days=2)
        bc2.class_type = 'beginner'
        bc2.event.state = 'open'
        bc2.event.save()
        bc2.save()

        response = self.client.post(reverse('programs:class_registration'), self.get_post_dict([self.event.id]), secure=True)

        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertContains(response, 'Student is already enrolled')

    def test_class_register_wait_no_card(self):
        # put a record in to the database
        cr = Registration(event=self.event,
                          student=Student.objects.get(pk=4),
                          pay_status='paid',
                          idempotency_key=str(uuid.uuid4()))
        cr.save()
        bc = cr.event.beginnerclass_set.last()
        bc.beginner_wait_limit = 10
        bc.save()

        u = User.objects.get(pk=2)
        u.is_staff = False
        u.save()

        # change user, then try to add 2 more beginner students. Since limit is 2 can't add.
        self.client.force_login(u)
        self.get_post_dict([self.event.id])
        self.post_dict['form-0-student'] = 2
        self.post_dict['form-1-student'] = 3
        self.post_dict['form-1-register'] = True
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)

        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 3)
        self.assertRedirects(response, reverse('payment:card_manage'))

    @patch('program_app.tasks.wait_list_email.delay')
    def test_class_register_wait_with_card(self, wait_list_email):
        # put a record in to the database
        cr = Registration(event=self.event,
                               student=Student.objects.get(pk=4),
                               pay_status='paid',
                               idempotency_key=str(uuid.uuid4()))
        cr.save()
        bc = cr.event.beginnerclass_set.last()
        bc.beginner_wait_limit = 10
        bc.class_type = 'beginner'
        bc.save()

        u = User.objects.get(pk=2)
        u.is_staff = False
        u.save()
        card = self.add_card(u)

        # change user, then try to add 2 more beginner students. Since limit is 2 can't add.
        self.client.force_login(u)
        self.get_post_dict([self.event.id])
        self.post_dict['form-0-student'] = 2
        self.post_dict['form-1-student'] = 3
        self.post_dict['form-1-register'] = True
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'wait')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 3)
        # self.assertContains(response, 'Not enough space available in this class')
        self.assertRedirects(response, reverse('programs:wait_list', kwargs={'event': bc.event.id}))
        wait_list_email.assert_called_with([cr[1].id, cr[2].id])

    # @tag('temp')
    def test_class_register_wait_twice(self):
        bc1 = BeginnerClass.objects.get(pk=1)
        bc1.class_type = 'beginner'
        bc1.beginner_limit = 0
        bc1.beginner_wait_limit = 10
        bc1.event.state = 'wait'

        bc1.event.save()
        bc1.save()
        students = [Student.objects.get(pk=2), Student.objects.get(pk=3)]
        for s in students:
            cr = Registration(
                event=bc1.event,
                student=s,
                pay_status="waiting",
                idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
                reg_time='2021-06-09',
                attended=False)
            cr.save()

        bc2 = BeginnerClass.objects.get(pk=2)
        bc2.class_type = 'beginner'
        bc2.beginner_limit = 0
        bc2.beginner_wait_limit = 10
        bc2.event.state = 'wait'
        bc2.event.event_date = (timezone.now() + timezone.timedelta(days=5)).replace(hour=11, minute=0, second=0)
        bc2.event.save()
        bc2.save()

        u = User.objects.get(pk=2)
        u.is_staff = False
        u.save()
        card = self.add_card(u)

        # change user, then try to add 2 more beginner students. Since limit is 2 can't add.
        self.client.force_login(u)
        self.get_post_dict([bc2.event.id])
        self.post_dict['form-0-student'] = 2
        self.post_dict['form-1-student'] = 3
        self.post_dict['form-1-register'] = True
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)
        # response = self.client.post(reverse('programs:class_registration'),
        #              {'event': '2', 'student_2': 'on', 'student_3': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(pk=2)
        self.assertEqual(bc.event.state, 'wait')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 2)
        self.assertContains(response, f'{students[0].first_name} is on wait list for another beginner class')

    def test_class_register_wait_and_no_wait(self):
        bc1 = BeginnerClass.objects.get(pk=1)
        bc1.class_type = 'beginner'
        bc1.beginner_limit = 2
        bc1.beginner_wait_limit = 10
        bc1.event.state = 'wait'
        bc1.event.save()
        bc1.save()
        students = [Student.objects.get(pk=2), Student.objects.get(pk=3)]
        for s in students:
            cr = Registration(
                event=bc1.event,
                student=s,
                pay_status="paid",
                idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
                reg_time='2021-06-09',
                attended=False)
            cr.save()

        bc2 = BeginnerClass.objects.get(pk=2)
        bc2.class_type = 'beginner'
        bc2.beginner_limit = 0
        bc2.beginner_wait_limit = 10
        bc2.event.state = 'wait'
        bc2.event.event_date = (timezone.now() + timezone.timedelta(days=5)).replace(hour=11, minute=0, second=0)
        bc2.event.save()
        bc2.save()

        u = User.objects.get(pk=2)
        u.is_staff = False
        u.save()
        card = self.add_card(u)

        # change user, then try to add 2 more beginner students. Since limit is 2 can't add.
        self.client.force_login(u)
        self.get_post_dict([bc2.event.id])
        self.post_dict['form-0-student'] = 2
        self.post_dict['form-1-student'] = 3
        self.post_dict['form-1-register'] = True
        response = self.client.post(reverse('programs:class_registration'), self.post_dict, secure=True)
        # response = self.client.post(reverse('programs:class_registration'),
        #              {'event': '2', 'student_2': 'on', 'student_3': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(pk=2)
        self.assertEqual(bc.event.state, 'wait')
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 4)
        self.assertRedirects(response, reverse('programs:wait_list', kwargs={'event': bc.event.id}))

    def test_resume_registration_wait_with_card(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 0
        bc.beginner_wait_limit = 10
        bc.event.state = 'wait'
        bc.event.save()
        bc.save()
        cr = Registration(
            event=bc.event,
            student=Student.objects.get(pk=4),
            pay_status="start",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)
        cr.save()
        card = self.add_card(self.test_user)

        response = self.client.get(reverse('programs:resume_registration', kwargs={'reg_id': cr.id}), secure=True)
        self.assertRedirects(response, reverse('programs:wait_list', kwargs={'event': bc.event.id}))

    def test_resume_registration_wait_no_card(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 0
        bc.beginner_wait_limit = 10
        bc.event.state = 'wait'
        bc.event.save()
        bc.save()
        cr = Registration(
            event=bc.event,
            student=Student.objects.get(pk=4),
            pay_status="start",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)
        cr.save()

        response = self.client.get(reverse('programs:resume_registration', kwargs={'reg_id': cr.id}), secure=True)
        self.assertRedirects(response, reverse('payment:card_manage'))
