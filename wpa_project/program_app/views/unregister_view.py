import logging
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import FormView
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response

from ..serializers import UnregisterSerializer
from payment.src import EmailMessage, RefundHelper
from ..src import ClassRegistrationHelper
from ..models import BeginnerClass, ClassRegistration
from ..forms import UnregisterForm
from student_app.models import Student
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
        # self.square_helper = SquareHelper()
        self.refund = RefundHelper()
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
            sf = Student.objects.get(user=request.user).student_family
            for s in sf.student_set.all():
                student_list.append(s.id)
            logging.debug(serializer.data)
            logging.debug(student_list)
            # idempotency_key = uuid.uuid4()
            self.ik_list = []
            class_list = serializer.data['class_list']
            donation = serializer.data.get('donation', False)
            errors = ""
            for c in class_list:
                # cr = get_object_or_404(ClassRegistration, pk=c)
                try:
                    cr = ClassRegistration.objects.get(pk=c)
                except (ClassRegistration.DoesNotExist, AttributeError):
                    logging.debug('registration not found')
                    response_dict['error'] = 'registration not found'
                    return Response(response_dict)
                dt = timezone.now() + timedelta(hours=24)

                if cr.beginner_class.state in BeginnerClass().get_states()[3:]:
                    logging.error(f'beginner class state is {cr.beginner_class.state}')
                    return Response(response_dict)
                logging.debug(cr.student.student_family.id)
                if cr.student.id not in student_list:
                    logging.error('not authorized')
                    return Response(response_dict)
                logging.debug(cr.pay_status)
                if cr.beginner_class.class_date < dt:
                    logging.debug('Time to unregister has passed.')
                    response_dict['error'] = 'Time to unregister has passed.'
                    return Response(response_dict)
                else:
                    self.add_key(cr.idempotency_key)
            if not donation:
                for ik in self.ik_list:

                    square_response = self.refund.refund_with_idempotency_key(ik.idempotency_key,
                                                                              ik.amount * 100 * ik.count)
                    if square_response['status'] == 'error':  # pragma: no cover
                        logging.error(square_response)
                        if type(square_response['error']) == str:
                            errors += square_response['error']
                        else:
                            logging.debug(type(square_response['error']))
                            logging.debug(square_response['error'])
            logging.debug(errors)
            if errors == '':
                response_dict['status'] = "SUCCESS"
                # update the number of enrolled students
                canceled_count = 0
                for c in class_list:
                    cr = ClassRegistration.objects.get(pk=c)
                    # if cr.beginner_class.state == 'full':
                    #     cr.beginner_class.state = 'open'
                    # cr.beginner_class.save()
                    if cr.pay_status == 'start' or cr.pay_status == 'canceled':
                        cr.pay_status = 'canceled'
                        canceled_count += 1
                    elif donation:
                        cr.pay_status = 'refund donated'
                    else:
                        cr.pay_status = 'refunded'
                    cr.save()
                    # ClassRegistrationHelper().check_space(
                    #     {'beginner_class': cr.beginner_class.id, 'beginner': 0, 'returnee': 0}, True)
                    ClassRegistrationHelper().update_class_state(cr.beginner_class)
                logging.debug(f'class_list length: {len(class_list)}, canceled_count: {canceled_count}')
                if len(class_list) > canceled_count:
                    EmailMessage().refund_email(request.user, donation)
            elif errors == 'Previously refunded':  # pragma: no cover  # we should remove them from the list anyway
                response_dict['status'] = "SUCCESS"
            else:  # pragma: no cover
                response_dict['status'] = "ERROR"
            return Response(response_dict)

        else:  # pragma: no cover
            logging.debug(serializer.errors)
            response_dict['error'] = 'unregister processing error'
            return Response(response_dict)


class UnregView(UserPassesTestMixin, FormView):
    template_name = 'program_app/forms/unregister.html'
    form_class = UnregisterForm
    success_url = reverse_lazy('registration:index')
    student_family = None

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        class_list = []
        for k, v in form.cleaned_data.items():
            if v:
                logging.debug(k.split('_'))
                class_list.append(int(k.split('_')[1]))
        logging.debug(class_list)
        cr = ClassRegistration.objects.filter(id__in=class_list).filter(pay_status='paid')
        if not self.request.user.is_board:
            cr = cr.filter(student__in=self.student_family.student_set.all())
        logging.debug(cr.values('idempotency_key').annotate(ik_count=Count('idempotency_key')).order_by())
        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['family'] = self.student_family
        # if self.request.user.is_board:
        #     kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.student_set.last() is not None:
            self.student_family = self.request.user.student_set.first().student_family
        return self.student_family is not None
