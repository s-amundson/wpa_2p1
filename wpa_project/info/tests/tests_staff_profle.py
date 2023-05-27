import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from event.models import Event, Registration
from student_app.models import User, Student
from ..models import StaffProfile
logger = logging.getLogger(__name__)


class TestsStaffProfile(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_staff_list(self):
        d = timezone.now() - timezone.timedelta(days=20)
        event = Event.objects.get(pk=1)
        event.event_date = event.event_date.replace(year=d.year, month=d.month, day=d.day)
        event.save()

        Registration.objects.create(
            event=event,
            student=Student.objects.get(pk=2),
            pay_status='paid',
            idempotency_key=str(uuid.uuid4()),
            attended=True,
            user=User.objects.get(pk=2),
        )

        response = self.client.get(reverse('information:staff_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 2)

    def test_get_staff_profile_form(self):
        response = self.client.get(reverse('information:staff_profile_form'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/preview_form.html')

    def test_post_staff_profile_form(self):
        response = self.client.post(reverse('information:staff_profile_form'),
                                    {'student': 1,
                                     'bio': 'Test bio',
                                     'status': 1})
        sp = StaffProfile.objects.all()
        self.assertEqual(len(sp), 1)
        self.assertEqual(sp[0].bio, 'Test bio')

    def test_post_staff_profile_form_id(self):
        osp = StaffProfile.objects.create(
            student=Student.objects.get(pk=1),
            bio='Original test bio',
            status=1
        )
        logger.warning(osp.id)
        response = self.client.post(reverse('information:staff_profile_form', kwargs={'pk': osp.id}),
                                    {'student': 1,
                                     'bio': 'Test bio',
                                     'status': 1}, secure=True)
        sp = StaffProfile.objects.all()
        self.assertEqual(len(sp), 1)
        self.assertEqual(sp[0].bio, 'Test bio')
