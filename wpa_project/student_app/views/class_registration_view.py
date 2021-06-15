import uuid

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone
import logging


from ..forms import ClassRegistrationForm
from ..models import BeginnerClass, ClassRegistration, Student, StudentFamily
from ..src import ClassRegistrationHelper, SquareHelper

logger = logging.getLogger(__name__)


class ClassRegisteredTable(LoginRequiredMixin, View):
    def get(self, request):
        try:
            students = StudentFamily.objects.get(user=request.user).student_set.all()
        except StudentFamily.DoesNotExist:
            request.session['message'] = 'Address form is required'
            return HttpResponseRedirect(reverse('registration:profile'))
        bc = BeginnerClass.objects.filter(state__in=BeginnerClass().get_states()[:3])
        enrolled_classes = ClassRegistration.objects.filter(student__in=students, beginner_class__in=bc).exclude(
            pay_status='refunded')
        logging.debug(enrolled_classes.values())
        return render(request, 'student_app/tables/class_registered_table.html', {'enrolled_classes': enrolled_classes})


class ClassRegistrationView(LoginRequiredMixin, View):
    def get(self, request, reg_id=None):
        try:
            students = StudentFamily.objects.get(user=request.user).student_set.all()
        except StudentFamily.DoesNotExist:
            request.session['message'] = 'Address form is required'
            logging.debug(request.session['message'])
            return HttpResponseRedirect(reverse('registration:student_register'))
        if reg_id:  # to regain an interrupted payment
            cr = get_object_or_404(ClassRegistration, pk=reg_id)
            logging.debug(f'Students: {students[0].student_family.id}, cr:{cr.student.student_family.id}')
            if cr.student.student_family != students[0].student_family:
                logging.error('registration mismatch')
                return Http404("registration mismatch")
            registrations = ClassRegistration.objects.filter(idempotency_key=cr.idempotency_key)
            request.session['idempotency_key'] = str(cr.idempotency_key)
            request.session['line_items'] = []
            request.session['payment_db'] = 'ClassRegistration'
            beginner = 0
            returnee = 0

            for r in registrations:
                logging.debug(r.student.id)
                request.session['line_items'].append(
                    SquareHelper().line_item(f"Class on {r.beginner_class.class_date} student id: {str(r.student.id)}", 1,
                                             r.beginner_class.cost))
                if r.student.safety_class is None:
                    beginner += 1
                else:
                    returnee += 1

            request.session['class_registration'] = {'beginner_class': r.beginner_class.id, 'beginner': beginner,
                                                     'returnee': returnee}
            return HttpResponseRedirect(reverse('registration:process_payment'))

        form = ClassRegistrationForm(students)
        return render(request, 'student_app/class_registration.html', {'form': form})

    def post(self, request):
        logging.debug(request.POST)
        students = StudentFamily.objects.filter(user=request.user)[0].student_set.all()

        form = ClassRegistrationForm(students, request.POST)
        logging.debug(form.data)
        if form.is_valid():
            logging.debug('valid')
            logging.debug(form.cleaned_data)

            beginner_class = BeginnerClass.objects.get(class_date=form.cleaned_data['beginner_class'])
            beginner = 0
            returnee = 0
            students = []
            message = ""
            for k,v in form.cleaned_data.items():
                if str(k).startswith('student_') and v:
                    i = int(str(k).split('_')[-1])
                    s = Student.objects.get(pk=i)
                    if len(ClassRegistration.objects.filter(beginner_class=beginner_class, student=s).exclude(
                            pay_status="refunded")) == 0:
                        if s.safety_class is None:
                            beginner += 1
                            students.append(s)
                        else:
                            returnee += 1
                            students.append(s)
                    else:
                        message += 'Student already enrolled'
            logging.debug(f'Beginner = {beginner}, returnee = {returnee}')
            request.session['class_registration'] = {'beginner_class': beginner_class.id, 'beginner': beginner,
                                                     'returnee': returnee}

            # logging.debug(list(c))
            if beginner_class.state == 'open':  # in case it changed since user got the form.
                enrolled_count = ClassRegistrationHelper().enrolled_count(beginner_class)
                logging.debug(enrolled_count)
                if enrolled_count['beginner'] + beginner > beginner_class.beginner_limit:
                    message += "to many beginners"
                if enrolled_count['returnee'] + returnee > beginner_class.returnee_limit:
                    message += 'to many returnee'
                if message == "":
                    return self.transact(beginner_class, request, students)

                else:
                    logging.debug(message)
                    return render(request, 'student_app/class_registration.html', {'form': form, 'message': message})

        else:
            logging.debug(form.errors)
            return render(request, 'student_app/class_registration.html', {'form': form})

        return HttpResponseRedirect(reverse('registration:profile'))

    def transact(self, beginner_class, request, students):
        with transaction.atomic():
            uid = str(uuid.uuid4())
            request.session['idempotency_key'] = uid
            request.session['line_items'] = []
            request.session['payment_db'] = 'ClassRegistration'

            for s in students:
                if s.safety_class is None:
                    n = True
                else:
                    n = False
                ClassRegistration(beginner_class=beginner_class, student=s, new_student=n,
                                  pay_status='start', idempotency_key=uid).save()
                request.session['line_items'].append(
                    SquareHelper().line_item(f"Class on {beginner_class.class_date} student id: {str(s.id)}", 1,
                                             beginner_class.cost))

        return HttpResponseRedirect(reverse('registration:process_payment'))

