import logging
from unittest.mock import patch
from django.apps import apps
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core import mail
from captcha.conf import settings as captcha_settings

from ..models import Category, Message, SpamWords
from ..tasks import send_contact_email
logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsMessage(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        self.settings(CAPTCHA_TEST_MODE=True)
        captcha_settings.CAPTCHA_TEST_MODE = True
        self.post_dict = {'contact_name': ['Emily Conlan'],
                          'email': ['EmilyNConlan@einrot.com'],
                          'category': ['2'],
                          'message': ['test message'],
                          'captcha_0': 'PASSED',
                          'captcha_1': 'PASSED',
                          }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        captcha_settings.CAPTCHA_TEST_MODE = False

    def _category_post(self):
        c = Category.objects.create(title='test category')
        c.recipients.set([self.test_user])
        self.post_dict['category'] = c.id

    def check_email(self):
        self.assertEqual(mail.outbox[0].subject, 'WPA Contact Us test category')
        self.assertTrue(mail.outbox[0].body.find('test message') > 0)

    def send_email(self, message_id):
        send_contact_email(message_id)

    def test_get_message_user(self):
        response = self.client.get(reverse('contact_us:contact'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/message.html')
        self.assertTrue(response.context['form'].has_instance)
        self.assertTrue(len(response.context['email']) > 5)

    def test_get_message_nonuser(self):
        self.client.logout()
        response = self.client.get(reverse('contact_us:contact'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/message.html')
        self.assertTrue(response.context['form'].has_instance)

    def test_get_message_board_existing_good(self):
        c = Category.objects.create(title='test category')
        c.recipients.set([self.test_user])
        message = Message.objects.create(category=c,
                                         contact_name=self.post_dict['contact_name'][0],
                                         email=self.post_dict['email'][0],
                                         message=self.post_dict['message'][0])
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:contact', kwargs={'message_id': message.id}), secure=True)
        self.assertFalse(response.context['form'].has_instance)

    @patch('contact_us.views.message_view.send_contact_email.delay')
    def test_post_message_user(self, sce):
        sce.side_effect = self.send_email
        self._category_post()
        response = self.client.post(reverse('contact_us:contact'), self.post_dict, secure=True)
        message = Message.objects.all()
        self.assertEqual(len(message), 1)
        self.check_email()

    def test_post_message_user_invalid(self):
        del self.post_dict['email']
        self._category_post()
        response = self.client.post(reverse('contact_us:contact'), self.post_dict, secure=True)
        message = Message.objects.all()

        self.assertEqual(len(message), 0)

    @patch('contact_us.views.message_view.send_contact_email.delay')
    def test_post_message_nonuser(self, sce):
        sce.side_effect = self.send_email
        self.client.logout()
        self._category_post()
        response = self.client.post(reverse('contact_us:contact'), self.post_dict, secure=True)
        message = Message.objects.all()
        self.assertEqual(len(message), 1)
        self.check_email()

    @patch('contact_us.views.message_view.send_contact_email.delay')
    def test_spam_message_spam_word(self, sce):
        sce.side_effect = self.send_email
        SpamWords.objects.create(word='porn')
        self.client.logout()
        self._category_post()
        self.post_dict['message'][0] = "This message has the evil word of Porn"
        logging.warning(self.post_dict)
        response = self.client.post(reverse('contact_us:contact'), self.post_dict, secure=True)
        message = Message.objects.all()
        self.assertEqual(len(message), 1)
        self.assertEqual(len(mail.outbox), 0)

    @patch('contact_us.views.message_view.send_contact_email.delay')
    def test_spam_message_ru(self, sce):
        sce.side_effect = self.send_email
        self.client.logout()
        self._category_post()
        self.post_dict['message'][0] = "This message has to many russian websites http://loan.tb.ru/bez-proverok http://loan.tb.ru/bez-procentov http://loan.tb.ru/mikrozajm"
        logging.warning(self.post_dict)
        response = self.client.post(reverse('contact_us:contact'), self.post_dict, secure=True)
        message = Message.objects.all()
        self.assertEqual(len(message), 1)
        self.assertEqual(len(mail.outbox), 0)

    @patch('contact_us.views.message_view.send_contact_email.delay')
    def test_spam_message_english(self, sce):
        sce.side_effect = self.send_email
        self.client.logout()
        self._category_post()
        # this was taken from an actual message.
        self.post_dict['message'][0] = """Народ подскажите как лучше сделать крышу на пристройке.
Верней даже из чего её надежней сделать. Нюанс есть один - кровля должна быть плоская. Такая у меня уж пристройка сделана.
Сейчас смотрел про кровди из мембраны ПВХ https://theballettheatre.com - тут, вроде как смотрится достойно и по надежности нормально, и по стоимости доступно.
Сталкивался ли кто-то из вас с такими кровлями? Какие там подводныекамни, прошу прояснить для нуба."""
        logging.warning(self.post_dict)
        response = self.client.post(reverse('contact_us:contact'), self.post_dict, secure=True)
        message = Message.objects.all()
        self.assertEqual(len(message), 1)
        self.assertEqual(len(mail.outbox), 0)

    @patch('contact_us.views.message_view.send_contact_email.delay')
    def test_message_english(self, sce):
        sce.side_effect = self.send_email
        self.client.logout()
        self._category_post()
        # this was taken from an actual message.
        self.post_dict['message'][0] = """Hello,

I would like to know if a group of 5 people can attend and could we get some instructions if some of us have little to no experience?  How would the cost work?

Thanks 
Julieta"""
        logging.warning(self.post_dict)
        response = self.client.post(reverse('contact_us:contact'), self.post_dict, secure=True)
        message = Message.objects.all()
        self.assertEqual(len(message), 1)
        self.assertEqual(len(mail.outbox), 1)


class TestsMessageList(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.post_dict = {'contact_name': ['Emily Conlan'], 'email': ['EmilyNConlan@einrot.com'], 'category': ['2'],
                          'message': ['test message']}

    def add_message(self):
        c = Category.objects.create(title='test category')
        c.recipients.set([User.objects.get(pk=3)])
        message = Message.objects.create(category=c,
                                         contact_name=self.post_dict['contact_name'][0],
                                         email=self.post_dict['email'][0],
                                         message=self.post_dict['message'][0])

    def test_get_list_auth(self):
        self.add_message()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:message_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/message_list.html')
        self.assertEqual(len(response.context['object_list']), 1)

    def test_get_list_auth_empty(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:message_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/message_list.html')
        self.assertEqual(len(response.context['object_list']), 0)

    def test_get_list_no_auth(self):
        self.add_message()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:message_list'), secure=True)
        self.assertEqual(response.status_code, 403)
