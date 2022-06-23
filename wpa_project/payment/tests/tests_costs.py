# import logging
# from django.apps import apps
# from django.test import TestCase, Client
# from django.urls import reverse
#
# from ..models import CostsModel
#
# logger = logging.getLogger(__name__)
# User = apps.get_model('student_app', 'User')
#
# class TestsCosts(TestCase):
#     fixtures = ['f1']
#
#     def setUp(self):
#         # Every test needs a client.
#         self.client = Client()
#         self.test_user = User.objects.get(pk=1)
#         self.client.force_login(self.test_user)
#         self.costs = {'name': "Test Cost", 'member_cost': 10, 'standard_cost': 20, 'membership': False, 'enabled': True}
#
#     def test_costs_get_page_forbidden(self):
#         # Get the page, if not super or board, page is forbidden
#         self.test_user = User.objects.get(pk=3)
#         self.client.force_login(self.test_user)
#         response = self.client.get(reverse('payment:costs'), secure=True)
#         self.assertEqual(response.status_code, 403)
#
#     def test_costs_get_page(self):
#         # Change user then Get the page
#         response = self.client.get(reverse('payment:costs'), secure=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('payment/costs.html')
#
#     def test_costs_new_cost(self):
#         response = self.client.post(reverse('payment:costs'), self.costs, secure=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('payment/costs.html')
#         cm = CostsModel.objects.get(pk=2)
#         self.assertEqual(cm.name, "Test Cost")
#         self.assertEqual(cm.member_cost, 10)
#         self.assertEqual(cm.standard_cost, 20)
#         self.assertFalse(cm.membership)
#         self.assertTrue(cm.enabled)
#
#     def test_costs_new_cost_invalid(self):
#         del self.costs['standard_cost']
#         response = self.client.post(reverse('payment:costs'), self.costs, secure=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('payment/costs.html')
#         cm = CostsModel.objects.all()
#         self.assertEqual(len(cm), 1)
#
#     def test_costs_edit_cost(self):
#         response = self.client.get(reverse('payment:costs', kwargs={'cost_id': 1}), secure=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('payment/costs.html')
#         response = self.client.post(reverse('payment:costs', kwargs={'cost_id': 1}), self.costs, secure=True)
#         cm = CostsModel.objects.all()
#         self.assertEqual(len(cm), 1)
#         cm = cm[0]
#         self.assertEqual(cm.name, "Test Cost")
#         self.assertEqual(cm.member_cost, 10)
#         self.assertEqual(cm.standard_cost, 20)
#         self.assertFalse(cm.membership)
#         self.assertTrue(cm.enabled)