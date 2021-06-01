import uuid

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone
import logging


from ..forms import ClassRegistrationForm
from ..models import BeginnerClass, ClassRegistration, Student, StudentFamily
from ..src.square_helper import line_item

logger = logging.getLogger(__name__)


class ClassRegistrationView(LoginRequiredMixin, View):
    def get(self, request):
        # classes = BeginnerClass.get_open_classes()
        students = StudentFamily.objects.filter(user=request.user)[0].student_set.all()
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
                    if len(ClassRegistration.objects.filter(beginner_class=beginner_class, student=s)) == 0:
                        if s.safety_class is None:
                            beginner += 1
                            students.append(s)
                        else:
                            returnee += 1
                            students.append(s)
                    else:
                        message += 'Student already enrolled'
            logging.debug(f'Beginner = {beginner}, returnee = {returnee}')

            # logging.debug(list(c))
            if beginner_class.state == 'open':  # in case it changed since user got the form.

                if beginner_class.enrolled_beginners + beginner <= beginner_class.beginner_limit:
                    beginner_class.enrolled_beginners += beginner
                else:
                    message += "to many beginners"
                if beginner_class.enrolled_returnee + returnee <= beginner_class.returnee_limit:
                    beginner_class.enrolled_returnee += returnee
                else:
                    logging.debug('to many returnee')
                    message += 'to many returnee'
                if message == "":
                    with transaction.atomic():
                        uid = str(uuid.uuid4())
                        if beginner_class.enrolled_beginners == beginner_class.beginner_limit and \
                            beginner_class.enrolled_returnee == beginner_class.returnee_limit:
                            beginner_class.state = 'full'
                        beginner_class.save()
                        logging.debug('save')
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
                            logging.debug(s.id)
                            request.session['line_items'].append(
                                line_item(f"Class on {beginner_class.class_date} student id: {str(s.id)}", 1,
                                          beginner_class.cost))
                    return HttpResponseRedirect(reverse('registration:process_payment'))

                else:
                    logging.debug(message)
                    return render(request, 'student_app/class_registration.html', {'form': form, 'message': message})
        #     enrolled_beginners = models.IntegerField(default=0)
        #     beginner_limit = models.IntegerField()
        #     enrolled_returnee = models.IntegerField(default=0)
        #     returnee_limit = models.IntegerField()

        else:
            logging.debug(form.errors)

        return HttpResponseRedirect(reverse('registration:profile'))
    #     beginner_class = models.ForeignKey(BeginnerClass, on_delete=models.SET_NULL, null=True)
    #     student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    #     new_student = models.BooleanField()
    #     pay_status = models.CharField(max_length=20)
    #     idempotency_key = models.UUIDField(default=str(uuid.uuid4()))
    #     reg_time = models.DateField()
