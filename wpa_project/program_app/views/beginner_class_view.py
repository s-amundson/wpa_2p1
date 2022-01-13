import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic import ListView
from django.utils import timezone
from django.contrib import messages
from django.forms import model_to_dict

from ..forms import BeginnerClassForm, ClassAttendanceForm
from ..models import BeginnerClass, ClassRegistration
from ..src import ClassRegistrationHelper
from payment.src import SquareHelper
from payment.models import CostsModel

logger = logging.getLogger(__name__)


class BeginnerClassView(UserPassesTestMixin, View):
    def get(self, request, beginner_class=None):
        alert_message = ''
        logging.debug('staff')
        attendee_form = False
        if beginner_class is not None:
            c = BeginnerClass.objects.get(id=beginner_class)
            form = BeginnerClassForm(instance=c)
            attendee_form = ClassAttendanceForm(c)
            logging.debug(attendee_form)
        else:
            try:
                c = BeginnerClass.objects.latest('class_date').class_date
                logging.debug(f'c = str(c), type = {type(c)}')
                c = c + timedelta(days=7)
            except BeginnerClass.DoesNotExist:  # pragma: no cover
                c = timezone.now()
                logging.debug('class does not exist')
            try:
                cost = CostsModel.objects.filter(name='Beginner Class', enabled=True)[:1] #[0].standard_cost
                # costs = get_list_or_404(CostsModel, name='Beginner Class', enabled=True)
                # logging.debug(cost.values())
                costs = cost[0].standard_cost
                logging.debug(costs)
            except (CostsModel.DoesNotExist, IndexError) as e:  # pragma: no cover
                costs = 0
                messages.add_message(request, messages.ERROR, 'cost does not exist')
                logging.error('cost does not exist')
            form = BeginnerClassForm(initial={'class_date': c, 'beginner_limit': 20, 'returnee_limit': 20,
                                              'state': 'scheduled', 'cost': costs})
        return render(request, 'program_app/beginner_class.html', {'form': form, 'attendee_form': attendee_form,
                                                                   'alert_message': alert_message})

    def post(self, request, beginner_class=None):
        logging.debug(request.POST)

        if beginner_class is not None: # we are updating a record.

            bc = BeginnerClass.objects.get(pk=beginner_class)
            form = BeginnerClassForm(request.POST, instance=bc)

        else:
            form = BeginnerClassForm(request.POST)

        if form.is_valid():
            # dont' add a class on a date that already has a class.
            if len(BeginnerClass.objects.filter(class_date=form.cleaned_data['class_date'])) > 0 \
                    and beginner_class is None:
                logging.debug('Class Exists')
                messages.add_message(request, messages.ERROR, 'A class at this time already exists')
                return render(request, 'student_app/form_as_p.html', {'form': form, 'message': 'Class Exists'})

            bc = form.save()
            logging.debug(bc.class_type)
            if bc.class_type == 'beginner' and bc.returnee_limit > 0:
                messages.add_message(request, messages.WARNING,
                                     "beginner class can't have a returnee limit greater then 0")
                bc.returnee_limit = 0
                bc.save()
            elif bc.class_type == 'returnee' and bc.beginner_limit > 0:
                messages.add_message(request, messages.WARNING,
                                     "returning class can't have a beginner limit greater then 0")
                bc.beginner_limit = 0
                bc.save()
            if bc.state == 'canceled':
                ec = ClassRegistrationHelper().enrolled_count(bc)
                square_helper = SquareHelper()
                # need to refund students if any
                logging.debug(f'beginners: {ec["beginner"]}, returnees: {ec["returnee"]}')
                cancel_error = False
                if ec["beginner"] > 0 or ec["returnee"] > 0:
                    cr = ClassRegistration.objects.filter(beginner_class__id=bc.id)
                    ik_list = []
                    for reg in cr:
                        if reg.idempotency_key not in ik_list:
                            ik_list.append(reg.idempotency_key)
                            qty = len(cr.filter(idempotency_key=reg.idempotency_key))
                            square_response = square_helper.refund_payment(reg.idempotency_key, qty * bc.cost)
                            if square_response['status'] == 'error':
                                if square_response['error'] != 'Previously refunded':  # pragma: no cover
                                    cancel_error = True
                                    logging.error(square_response)
                                    messages.add_message(request, messages.ERROR, square_response)
                            else:
                                for c in cr.filter(idempotency_key=reg.idempotency_key):
                                    c.pay_status = 'refund'
                                    c.save()

                    logging.debug(cr)
                if not cancel_error:
                    messages.add_message(request, messages.SUCCESS, 'Class was canceled')

            return HttpResponseRedirect(reverse('programs:class_list'))
        else:
            logging.debug(form.errors)
            return render(request, 'program_app/beginner_class.html', {'form': form})

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        else:
            return False


class BeginnerClassListView(LoginRequiredMixin, ListView):
    template_name = 'program_app/beginner_class_list.html'

    def get_queryset(self):
        crh = ClassRegistrationHelper()
        bc = BeginnerClass.objects.filter(
            class_date__gte=timezone.localtime(timezone.now()).date()).order_by('class_date')
        queryset = []
        for c in bc:
            d = model_to_dict(c)
            d = {**d, **crh.enrolled_count(c)}
            queryset.append(d)
        return queryset
