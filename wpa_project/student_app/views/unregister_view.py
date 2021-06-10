import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from ..serializers import UnregisterSerializer
from ..src.square_helper import SquareHelper
from ..models import BeginnerClass, ClassRegistration, StudentFamily
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
        self.ik_list = []

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
                if cr.beginner_class.state in BeginnerClass().get_states()[3:]:
                    logging.error(f'beginner class state is {cr.beginner_class.state}')
                if cr.student.student_family.id not in student_list:
                    logging.error('not authorized')
                    return Response(response_dict)
                self.add_key(cr.idempotency_key)
            for ik in self.ik_list:
                square_response = self.square_helper.refund_payment(ik.idempotency_key, ik.amount * ik.count)
                if square_response['status'] == 'error':
                    logging.error(square_response)
                    errors += square_response['error']

            if errors == '':
                response_dict['status'] = "SUCCESS"
                # update the number of enrolled students
                for c in class_list:
                    cr = ClassRegistration.objects.get(pk=c)
                    if cr.student.safety_class is None:
                        cr.beginner_class.enrolled_beginners -= 1
                    else:
                        cr.beginner_class.enrolled_returnee -= 1
                    if cr.beginner_class.state == 'full':
                        cr.beginner_class.state = 'open'
                    cr.beginner_class.save()
                    cr.pay_status = 'refunded'
                    cr.save()
                # TODO email refund
            else:
                response_dict['status'] = "ERROR"
            return Response(response_dict)

        else:
            logging.debug(serializer.errors)
            response_dict['error'] = 'unregister processing error'
            return Response(response_dict)
