import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic import ListView
from django.utils import timezone
# from django.db.models import model
# from django.core.exceptions import ObjectDoesNotExist

from ..forms import BeginnerClassForm, ClassAttendanceForm
from ..models import BeginnerClass, Student

logger = logging.getLogger(__name__)


class BeginnerClassView(LoginRequiredMixin, View):
    def get(self, request, beginner_class=None):
        if not request.user.is_staff:
            return HttpResponseForbidden()
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
            form = BeginnerClassForm(initial={'class_date': c, 'beginner_limit': 20, 'returnee_limit': 20,
                                              'state': 'scheduled'})
        return render(request, 'student_app/beginner_class.html', {'form': form, 'attendee_form': attendee_form})

    def post(self, request, beginner_class=None):
        if not request.user.is_staff:
            return HttpResponseForbidden()
        logging.debug(request.POST)
        if 'attendee_form' in request.POST:
            c = BeginnerClass.objects.get(id=beginner_class)
            class_registration = c.classregistration_set.all()
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

            form.save()
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