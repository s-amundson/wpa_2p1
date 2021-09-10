import logging
import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.utils.datetime_safe import date
from django.contrib import messages
from ..forms import MembershipForm
from ..models import Level
from payment.src import SquareHelper
from student_app.models import Student

logger = logging.getLogger(__name__)


class MembershipView(LoginRequiredMixin, View):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.table = LevelModel.objects.all()

    def get(self, request):
        sf = Student.objects.get(user=request.user).student_family
        forms = []
        forms.append(MembershipForm(students=sf.student_set.all()))
        levels = Level.objects.filter(enabled=True)
        return render(request, 'membership/membership.html', {'forms': forms, 'levels': levels})

    def post(self, request):
        logging.debug(request.POST)
        sf = Student.objects.get(user=request.user).student_family
        students = sf.student_set.all()
        form = MembershipForm(students, request.POST)
        if form.is_valid():
            logging.debug(form.cleaned_data)
            members = []
            for s in students:
                if form.cleaned_data.get(f'student_{s.id}', False):
                    members.append(s)
            logging.debug(members)
            logging.debug(len(members))
            level = form.cleaned_data.get('level', None)
            if len(members) == 0:
                logging.debug('nobody selected')
                messages.add_message(request, messages.ERROR, 'no students selected')
            elif len(members) > 1:

                if len(members) > 4:
                    cost = level.cost + (level.additional_cost * (len(members) - 4))
                else:
                    cost = level.cost
                if not level.is_family:
                    logging.debug('multiple members not family')
                    messages.add_message(request, messages.ERROR, 'incorrect membership selected')
                else:
                    self.transact(form, request, members, cost)
                    return HttpResponseRedirect(reverse('payment:process_payment'))

            else:
                max_age = 999
                if level.max_age is not None:
                    max_age = level.max_age
                min_age = 0
                if level.min_age is not None:
                    min_age = level.min_age

                member = members[0]
                age = date.today().year - member.dob.year
                logging.debug(age)

                if age > max_age:
                    logging.debug("to old for this membership")
                    messages.add_message(request, messages.ERROR, 'incorrect membership selected')
                elif age < min_age:
                    logging.debug("to young for this membership")
                    messages.add_message(request, messages.ERROR, 'incorrect membership selected')
                else:
                    self.transact(form, request, members, level.cost)
                    return HttpResponseRedirect(reverse('payment:process_payment'))

        else:  # pragma: no cover
            logging.debug(form.errors)
            messages.add_message(request, messages.ERROR, 'other membership error')
        levels = Level.objects.filter(enabled=True)
        return render(request, 'membership/membership.html', {'forms': [form], 'levels': levels})

    def transact(self, form, request, members, cost):
        uid = str(uuid.uuid4())
        membership = form.save(commit=False)
        membership.pay_status = 'start'
        membership.idempotency_key = uid
        membership.save()
        for m in members:
            membership.students.add(m)

        request.session['idempotency_key'] = uid
        request.session['line_items'] = [SquareHelper().line_item(f"{membership.level.name} Membership", 1, cost)]
        request.session['payment_db'] = ['membership', 'Membership']
        membership.save()
