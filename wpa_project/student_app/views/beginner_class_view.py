import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_list_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic import ListView
from django.utils import timezone
# from django.db.models import model
# from django.core.exceptions import ObjectDoesNotExist

from ..forms import BeginnerClassForm, ClassAttendanceForm
from ..models import BeginnerClass, ClassRegistration, CostsModel
from ..src import SquareHelper

logger = logging.getLogger(__name__)


class BeginnerClassView(LoginRequiredMixin, View):
    def get(self, request, beginner_class=None):
        if not request.user.is_staff:
            return HttpResponseForbidden()
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
            try:
                cost = CostsModel.objects.filter(name='Beginner Class', enabled=True)[:1] #[0].standard_cost
                costs = get_list_or_404(CostsModel, name='Beginner Class', enabled=True)
                costs = cost[0]
                logging.debug(costs)
            except CostsModel.DoesNotExist:
                cost = 0
                logging.error('cost does not exist')
            form = BeginnerClassForm(initial={'class_date': c, 'beginner_limit': 20, 'returnee_limit': 20,
                                              'state': 'scheduled', 'cost': cost})
        return render(request, 'student_app/beginner_class.html', {'form': form, 'attendee_form': attendee_form})

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
                    registration.student.safety_class = str(c.class_date)
                    new_count += 1

                elif registration.attended: # if registration was unchecked remove safety class date.
                    logging.debug('remove attendance')
                    registration.student.safety_class = None
                    registration.attended = False
                registration.student.save()
                registration.save()
            logging.debug(new_count)
            return HttpResponseRedirect(reverse('registration:index'))
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
                return render(request, 'student_app/form_as_p.html', {'form': form, 'message': 'Class Exists'})

            bc = form.save()
            if bc.state == 'canceled':
                square_helper = SquareHelper()
                # need to refund students if any
                logging.debug(f'beginners: {bc.enrolled_beginners}, returnees: {bc.enrolled_returnee}')
                if bc.enrolled_beginners > 0 or bc.enrolled_returnee > 0:
                    cr = ClassRegistration.objects.filter(beginner_class__id=bc.id)
                    for reg in cr.distinct('idempotency_key'):
                        qty = len(cr.filter(reg.idempotency_key))
                        square_response = square_helper.refund_payment(reg.idempotency_key, qty * reg.cost)
                        if square_response['status'] == 'error':
                            logging.error(square_response)

                    logging.debug(cr)

            return HttpResponseRedirect(reverse('registration:index'))
        else:
            logging.debug(form.errors)
            return render(request, 'student_app/form_as_p.html', {'form': form})


class BeginnerClassListView(LoginRequiredMixin, ListView):
    template_name = 'student_app/beginner_class_list.html'
    queryset = BeginnerClass.objects.filter(class_date__gt=timezone.now())

    #     class_date = models.DateField()
    #     enrolled_beginners = models.IntegerField(default=0)
    #     beginner_limit = models.IntegerField()
    #     enrolled_returnee = models.IntegerField(default=0)
    #     returnee_limit = models.IntegerField()
    #     c = [('scheduled', 'scheduled'), ('open', 'open'), ('full', 'full'), ('closed', 'closed'), ('canceled', 'canceled')]
    #     state = models.CharField(max_length=20, null=True, choices=c)