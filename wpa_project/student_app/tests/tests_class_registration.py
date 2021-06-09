import logging

from django.test import TestCase, Client
from django.urls import reverse

from ..models import BeginnerClass, ClassRegistration, User

logger = logging.getLogger(__name__)


class TestsClassRegistration(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)

    def test_class_register(self):
        # Get the page
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('registration:class_registration'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/form_as_p.html')

        # add a user to the class with error
        self.client.post(reverse('registration:class_registration'), {'beginner_class': '2022-06', 'student_1': 'on'}, secure=True)
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc[0].enrolled_beginners, 0)
        self.assertEqual(bc[0].enrolled_returnee, 0)
        self.assertEqual(bc[0].state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 0)

        # add a user to the class
        self.client.post(reverse('registration:class_registration'), {'beginner_class': '2022-06-05', 'student_1': 'on'}, secure=True)
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc[0].enrolled_beginners, 1)
        self.assertEqual(bc[0].enrolled_returnee, 0)
        self.assertEqual(bc[0].state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertEqual(cr[0].beginner_class, bc[0])
        self.assertEqual(self.client.session['line_items'][0]['name'],
                         'Class on 2022-06-05 student id: 1')
        self.assertEqual(self.client.session['payment_db'], 'ClassRegistration')
        # self.assertRedirects(response, reverse('registration:index'))
        # self.assertRedirects(response, reverse('registration:process_payment'))
        self.client.get(reverse('registration:class_registration'), secure=True)

        # change user, then try to add 2 more beginner students. Since limit is 2 can't add.
        self.client.force_login(User.objects.get(pk=2))
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': '2022-06-05', 'student_2': 'on', 'student_3': 'on'}, secure=True)
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc[0].enrolled_beginners, 1)
        self.assertEqual(bc[0].enrolled_returnee, 0)
        self.assertEqual(bc[0].state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 1)


        # try to add first user to class again.
        logging.debug('add user again')
        self.client.force_login(User.objects.get(pk=1))
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': '2022-06-05', 'student_1': 'on'})

        # self.assertContains(response, 'Student already enrolled')
        # self.assertEqual(response.context['message'] == "")
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc[0].enrolled_beginners, 1)
        self.assertEqual(bc[0].enrolled_returnee, 0)
        self.assertEqual(bc[0].state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 1)

        # change user, then add 1 beginner students and 1 returnee.
        self.client.force_login(User.objects.get(pk=3))
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': '2022-06-05', 'student_4': 'on', 'student_5': 'on'}, secure=True)
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc[0].enrolled_beginners, 2)
        self.assertEqual(bc[0].enrolled_returnee, 1)
        self.assertEqual(bc[0].state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 3)

        # don't change user, try to add user not in family to class
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': '2022-06-05', 'student_6': 'on'}, secure=True)
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc[0].enrolled_beginners, 2)
        self.assertEqual(bc[0].enrolled_returnee, 1)
        self.assertEqual(bc[0].state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 3)

        # change user, then add 1 returnee.
        self.client.force_login(User.objects.get(pk=4))
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': '2022-06-05', 'student_6': 'on'}, secure=True)
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc[0].enrolled_beginners, 2)
        self.assertEqual(bc[0].enrolled_returnee, 2)
        self.assertEqual(bc[0].state, 'full')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 4)
