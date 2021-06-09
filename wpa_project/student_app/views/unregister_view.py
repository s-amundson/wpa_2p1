import logging
import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from square.client import Client
from ..serializers import UnregisterSerializer
from ..src.square_helper import SquareHelper
from ..models import ClassRegistration, StudentFamily
logger = logging.getLogger(__name__)


class UnregisterView(LoginRequiredMixin, APIView):
    class Reg:
        def __init__(self, idempotency_key):
            self.idempotency_key = idempotency_key
            self.count = 1
            cr = ClassRegistration.objects.filter(idempotency_key=idempotency_key)
            self.qty = len(cr)
            self.amount = cr[0].beginner_class.cost
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self):
        self.square_helper = SquareHelper()

    def add_key(self, key):
        if len(self.ik_list) == 0:
            self.ik_list.append(self.Reg(key))
        else:
            for ik in self.ik_list:
                if ik.idempotency_key == key:
                    ik.count += 1
                    return
            self.ik_list.append(self.Reg(key))
            return

    def post(self, request, format=None):
        response_dict = {'status': 'ERROR', 'receipt_url': '', 'error': ''}
        logging.debug(request.data)

        serializer = UnregisterSerializer(data=request.data)
        if serializer.is_valid():
            student_list = []
            sf = StudentFamily.objects.filter(user=request.user)
            for s in sf:
                student_list.append(s.id)
            logging.debug(serializer.data)
            # idempotency_key = uuid.uuid4()
            self.ik_list = []
            class_list = serializer.data['class_list']
            errors = ""
            for c in class_list:
                cr = ClassRegistration.objects.get(pk=c)
                if cr.student.student_family.id not in student_list:
                    logging.error('not authorized')
                    return Response(response_dict)
                # ClassRegistration.objects.filter(student.student_family__in=sf)
                # self.add_key(cr.idempotency_key)
        #     for ik in self.ik_list:
        #         square_response = self.square_helper.refund_payment(ik.idempotency_key, ik.amount * ik.count)
        #         if square_response['status'] != 'error':
        #             logging.error(square_response)
        #             errors += square_response['error']
        #         # if ik.qty == ik.count:
        #         #     logging.debug('refund order')
        #         #
        #         # else:
        #         #     logging.debug('refund partial')
        #
        #     if errors == '':
        #         response_dict['status'] = "SUCCESS"
        #     else:
        #         response_dict['status'] = "ERROR"
        #     return Response(response_dict)
        #
        # else:
        #     logging.debug(serializer.errors)
        #     response_dict['error'] = 'payment processing error'
        #     return JsonResponse(response_dict)
        return Response(response_dict)


