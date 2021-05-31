import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic import ListView
from django.utils import timezone
# from django.db.models import model
# from django.core.exceptions import ObjectDoesNotExist

from ..forms import BeginnerClassForm
from ..models import BeginnerClass

logger = logging.getLogger(__name__)


class BeginnerClassView(LoginRequiredMixin, View):
    # TODO make staff only
    def get(self, request, beginner_class=None):
        if beginner_class is not None:
            c = BeginnerClass.objects.get(id=beginner_class)
            form = BeginnerClassForm(instance=c)
        else:
            try:
                c = BeginnerClass.objects.latest('class_date').class_date
                logging.debug(f'c = str(c), type = {type(c)}')
                c = c + timedelta(days=7)
            except BeginnerClass.DoesNotExist:
                c = timezone.now()
            form = BeginnerClassForm(initial={'class_date': c, 'beginner_limit': 20, 'returnee_limit': 20,
                                              'state': 'scheduled'})
        return render(request, 'student_app/form_as_p.html', {'form': form})

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