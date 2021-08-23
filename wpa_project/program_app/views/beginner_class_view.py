import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic import ListView
from django.utils import timezone
from django.contrib import messages

from ..forms import BeginnerClassForm, ClassAttendanceForm
from ..models import BeginnerClass, ClassRegistration
from ..src import ClassRegistrationHelper
from payment.src import SquareHelper
from payment.models import CostsModel

logger = logging.getLogger(__name__)


class BeginnerClassView(LoginRequiredMixin, View):
    def get(self, request, beginner_class=None):
        if not request.user.is_staff:
            return HttpResponseForbidden()
        # messages.add_message(request, messages.INFO, 'Hello world.')
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
            except BeginnerClass.DoesNotExist:
                c = timezone.now()
                logging.debug('class does not exist')
            try:
                cost = CostsModel.objects.filter(name='Beginner Class', enabled=True)[:1] #[0].standard_cost
                # costs = get_list_or_404(CostsModel, name='Beginner Class', enabled=True)
                # logging.debug(cost.values())
                costs = cost[0].standard_cost
                logging.debug(costs)
            except (CostsModel.DoesNotExist, IndexError) as e:
                costs = 0
                messages.add_message(request, messages.ERROR, 'cost does not exist')
                logging.error('cost does not exist')
            form = BeginnerClassForm(initial={'class_date': c, 'beginner_limit': 20, 'returnee_limit': 20,
                                              'state': 'scheduled', 'cost': costs})
        return render(request, 'program_app/beginner_class.html', {'form': form, 'attendee_form': attendee_form,
                                                                   'alert_message': alert_message})

    def post(self, request, beginner_class=None):

        if not request.user.is_staff:
            return HttpResponseForbidden()
        logging.debug(request.POST)
        if 'attendee_form' in request.POST:
            c = BeginnerClass.objects.get(id=beginner_class)
            class_registration = c.classregistration_set.exclude(pay_status='refunded')
            new_count = 0
            for registration in class_registration:
                if f'check_{registration.student.id}' in request.POST:
                    registration.attended = True
                    registration.student.safety_class = str(c.class_date)[:10]
                    new_count += 1

                elif registration.attended: # if registration was unchecked remove safety class date.
                    logging.debug('remove attendance')
                    registration.student.safety_class = None
                    registration.attended = False
                registration.student.save()
                registration.save()
            logging.debug(new_count)
            return HttpResponseRedirect(reverse('programs:class_list'))
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
                messages.add_message(request, messages.ERROR, 'A class on this date already exists')
                return render(request, 'student_app/form_as_p.html', {'form': form, 'message': 'Class Exists'})

            bc = form.save()
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
                        #     pass
                        # else:
                            ik_list.append(reg.idempotency_key)
                            qty = len(cr.filter(idempotency_key=reg.idempotency_key))
                            square_response = square_helper.refund_payment(reg.idempotency_key, qty * bc.cost)
                            if square_response['status'] == 'error':
                                if square_response['error'] != 'Previously refunded':
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


class BeginnerClassListView(LoginRequiredMixin, ListView):
    template_name = 'program_app/beginner_class_list.html'
    queryset = BeginnerClass.objects.filter(class_date__gt=timezone.now())

    #     class_date = models.DateField()
    #     enrolled_beginners = models.IntegerField(default=0)
    #     beginner_limit = models.IntegerField()
    #     enrolled_returnee = models.IntegerField(default=0)
    #     returnee_limit = models.IntegerField()
    #     c = [('scheduled', 'scheduled'), ('open', 'open'), ('full', 'full'), ('closed', 'closed'), ('canceled', 'canceled')]
    #     state = models.CharField(max_length=20, null=True, choices=c)