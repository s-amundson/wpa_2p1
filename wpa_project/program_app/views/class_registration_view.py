import uuid
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import View
import logging


from ..forms import ClassRegistrationForm
from ..models import BeginnerClass, ClassRegistration
from ..src import ClassRegistrationHelper
from payment.src import SquareHelper

logger = logging.getLogger(__name__)
Student = apps.get_model(app_label='student_app', model_name='Student')
StudentFamily = apps.get_model(app_label='student_app', model_name='StudentFamily')


class ClassRegisteredTable(LoginRequiredMixin, View):
    def get(self, request):
        try:
            students = Student.objects.get(user=request.user).student_family.student_set.all()
        except (Student.DoesNotExist, AttributeError):
            request.session['message'] = 'Address form is required'
            return HttpResponseRedirect(reverse('registration:profile'))
        bc = BeginnerClass.objects.filter(state__in=BeginnerClass().get_states()[:3],
                                          class_date__gte=timezone.localdate(timezone.now()))
        enrolled_classes = ClassRegistration.objects.filter(student__in=students, beginner_class__in=bc).exclude(
            pay_status='refunded').exclude(pay_status='canceled')
        logging.debug(enrolled_classes.values())
        return render(request, 'program_app/tables/class_registered_table.html', {'enrolled_classes': enrolled_classes})


class ClassRegistrationView(LoginRequiredMixin, View):
    def get(self, request, reg_id=None):
        try:
            students = Student.objects.get(user=request.user).student_family.student_set.all()
        except (Student.DoesNotExist, AttributeError):
            request.session['message'] = 'Address form is required'
            # logging.debug(request.session['message'])
            return HttpResponseRedirect(reverse('registration:profile'))
        if reg_id:  # to regain an interrupted payment
            cr = get_object_or_404(ClassRegistration, pk=reg_id)
            logging.debug(f'Students: {students[0].student_family.id}, cr:{cr.student.student_family.id}')
            if cr.student.student_family != students[0].student_family:
                # logging.error('registration mismatch')
                return Http404("registration mismatch")
            registrations = ClassRegistration.objects.filter(idempotency_key=cr.idempotency_key)
            request.session['idempotency_key'] = str(cr.idempotency_key)
            request.session['line_items'] = []
            request.session['payment_db'] = ['program_app', 'ClassRegistration']
            request.session['action_url'] = reverse('programs:class_payment')
            beginner = 0
            returnee = 0

            for r in registrations:
                # logging.debug(r.student.id)
                logging.debug(r.beginner_class.class_date)
                request.session['line_items'].append(
                    SquareHelper().line_item(f"Class on {str(r.beginner_class.class_date)[:10]} student id: {str(r.student.id)}", 1,
                                             r.beginner_class.cost))
                if r.student.safety_class is None:
                    beginner += 1
                else:
                    returnee += 1

            request.session['class_registration'] = {'beginner_class': r.beginner_class.id, 'beginner': beginner,
                                                     'returnee': returnee}
            return HttpResponseRedirect(reverse('payment:process_payment'))

        form = ClassRegistrationForm(students)
        tm = timezone.localtime(timezone.now()).month
        return render(request, 'program_app/class_registration.html', {'form': form, 'this_month': tm})

    def post(self, request):
        students = Student.objects.get(user=request.user).student_family.student_set.all()
        logging.debug(request.POST)
        form = ClassRegistrationForm(students, request.POST)
        if form.is_valid():
            beginner_class = BeginnerClass.objects.get(pk=form.cleaned_data['beginner_class'])
            beginner = 0
            returnee = 0
            instructor = 0
            students = []
            instructors = []
            message = ""
            logging.debug(form.cleaned_data)
            for k, v in form.cleaned_data.items():
                logging.debug(k)
                if str(k).startswith('student_') and v:
                    i = int(str(k).split('_')[-1])
                    s = Student.objects.get(pk=i)
                    try:
                        is_instructor = s.user.is_instructor
                        instructor_expire = s.user.instructor_expire_date
                    except (s.DoesNotExist, AttributeError):
                        is_instructor = False
                        instructor_expire = None

                    logging.debug(s)
                    if ClassRegistrationHelper().calc_age(s, beginner_class.class_date) < 9:
                        messages.add_message(request, messages.ERROR, 'Student must be at least 9 years old to participate')
                        message += 'Student must be at least 9 years old to participate'
                        logging.debug(message)
                        HttpResponseRedirect(reverse('programs:class_registration'))
                    elif request.user.is_instructor and is_instructor:
                        logging.debug('user is instructor')
                        logging.debug(instructor_expire)
                        if instructor_expire is None or instructor_expire < timezone.localdate(timezone.now()):
                            messages.add_message(request, messages.ERROR,
                                                 'Please update your instructor certification')
                            message += 'Please update your instructor certification'
                            logging.debug(message)
                            HttpResponseRedirect(reverse('programs:class_registration'))
                        if len(ClassRegistration.objects.filter(beginner_class=beginner_class, student=s).exclude(
                                pay_status="refunded").exclude(pay_status='canceled')) == 0:
                            instructor += 1
                            instructors.append(s)
                        else:
                            messages.add_message(request, messages.ERROR,
                                                 'Instructor is already enrolled')
                            message += 'Instructor is already enrolled'
                    else:
                        if len(ClassRegistration.objects.filter(beginner_class=beginner_class, student=s).exclude(
                                pay_status="refunded").exclude(pay_status='canceled')) == 0:
                            if s.safety_class is None:
                                beginner += 1
                                students.append(s)
                            else:
                                returnee += 1
                                students.append(s)
                        else:
                            messages.add_message(request, messages.ERROR,
                                                 'Student is already enrolled')
                            message += 'Student is already enrolled'
            request.session['class_registration'] = {'beginner_class': beginner_class.id, 'beginner': beginner,
                                                     'returnee': returnee}

            logging.debug(beginner_class.state)
            if beginner_class.state == 'open':  # in case it changed since user got the form.
                enrolled_count = ClassRegistrationHelper().enrolled_count(beginner_class)
                if beginner and enrolled_count['beginner'] + beginner > beginner_class.beginner_limit:
                    messages.add_message(request, messages.ERROR,
                                         'Not enough space available in this class')
                    message += "Not enough space available in this class"
                if returnee and enrolled_count['returnee'] + returnee > beginner_class.returnee_limit:
                    messages.add_message(request, messages.ERROR,
                                         'Not enough space available in this class')
                    message += 'Not enough space available in this class'
                if instructor and enrolled_count['instructors'] + instructor > beginner_class.instructor_limit:
                    messages.add_message(request, messages.ERROR,
                                         'Not enough space available in this class')
                    message += 'Not enough space available in this class'
                if message == "":
                    logging.debug(message)
                    return self.transact(beginner_class, request, students, instructors)

                else:
                    logging.debug(message)
                    tm = timezone.localtime(timezone.now()).month
                    return render(request, 'program_app/class_registration.html',
                                  {'form': form, 'alert_message': message, 'this_month': tm})

        else:
            logging.debug(form.errors)
            return render(request, 'program_app/class_registration.html',
                          {'form': form, 'alert_message': 'This form has errors'})

        # return HttpResponseRedirect(reverse('registration:profile'))

    def transact(self, beginner_class, request, students, instructors):
        with transaction.atomic():
            uid = str(uuid.uuid4())
            request.session['idempotency_key'] = uid
            request.session['line_items'] = []
            request.session['payment_db'] = ['program_app', 'ClassRegistration']
            request.session['action_url'] = reverse('programs:class_payment')
            logging.debug(students)
            for s in students:
                if s.safety_class is None:
                    n = True
                else:
                    n = False
                cr = ClassRegistration(beginner_class=beginner_class, student=s, new_student=n,
                                  pay_status='start', idempotency_key=uid).save()
                request.session['line_items'].append(
                    SquareHelper().line_item(f"Class on {str(beginner_class.class_date)[:10]} student id: {str(s.id)}",
                                             1, beginner_class.cost))
                logging.debug(cr)
            for i in instructors:
                cr = ClassRegistration(beginner_class=beginner_class, student=i, new_student=False, pay_status='paid',
                                       idempotency_key=uid).save()
                request.session['line_items'].append(
                    SquareHelper().line_item(f"Class on {str(beginner_class.class_date)[:10]} instructor id: {str(i.id)}",
                                             1, 0))

        return HttpResponseRedirect(reverse('payment:process_payment'))

