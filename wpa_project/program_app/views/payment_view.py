# import logging
# from rest_framework.response import Response
#
# from payment.views import PaymentView
# from ..src import ClassRegistrationHelper
#
# logger = logging.getLogger(__name__)
#
#
# class PaymentView(PaymentView):
#     def __init__(self):
#         self.class_helper = ClassRegistrationHelper()
#         self.PV = super()
#         self.PV.__init__()
#
#     def post(self, request, format=None):
#         response_dict = {'status': 'ERROR', 'receipt_url': '', 'error': '', 'continue': False}
#         d = request.session.get('class_registration', None)
#         if d is not None:
#             if not self.class_helper.check_space(d, True):
#                 response_dict['error'] = 'not enough space in the class'
#                 return Response(response_dict)
#         return self.PV.post(request, format)
