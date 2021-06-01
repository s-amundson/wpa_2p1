from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
import logging


from ..forms import ClassRegistrationForm
from ..models import BeginnerClass, Student, StudentFamily

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
            beginner = 0
            returnee = 0
            for k,v in form.cleaned_data.items():
                if str(k).startswith('student_') and v:
                    i = int(str(k).split('_')[-1])
                    if Student.objects.get(pk=i).safety_class is None:
                        beginner += 1
                    else:
                        returnee += 1
            logging.debug(f'Beginner = {beginner}, returnee = {returnee}')
            c = BeginnerClass.objects.get(class_date=form.cleaned_data['beginner_class'])
            # logging.debug(list(c))
            if c.state == 'open':  # in case it changed since user got the form.
                message = ""
                if c.enrolled_beginners + beginner < c.beginner_limit:
                    c.enrolled_beginners += beginner
                else:
                    logging.debug("to many beginners")
                    message += "to many beginners"
                if c.enrolled_returnee + returnee < c.returnee_limit:
                    c.enrolled_returnee += returnee
                else:
                    logging.debug('to many returnee')
                    message += 'to many returnee'
                if message == "":
                    c.save()
                    logging.debug('save')
                else:
                    logging.debug(message)
        #             enrolled_beginners = models.IntegerField(default=0)
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