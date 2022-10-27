import logging
import uuid

from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.utils.datetime_safe import date
from ..forms import MembershipForm
from ..models import Level

logger = logging.getLogger(__name__)


class MembershipView(UserPassesTestMixin, FormView):
    template_name = 'membership/membership.html'
    form_class = MembershipForm
    students = None
    success_url = reverse_lazy('payment:make_payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['levels'] = Level.objects.filter(enabled=True)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['students'] = self.students
        return kwargs

    def form_invalid(self, form):
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.warning(form.cleaned_data)
        members = []
        for s in self.students:
            if form.cleaned_data.get(f'student_{s.id}', False):
                members.append(s)
        level = form.cleaned_data.get('level', None)
        if len(members) == 0:
            logging.debug('nobody selected')
            form.add_error(None, 'No students selected')
            return self.form_invalid(form)
        elif len(members) > 1:

            if len(members) > 4:
                cost = level.cost + (level.additional_cost * (len(members) - 4))
            else:
                cost = level.cost
            if not level.is_family:
                logging.debug('multiple members not family')
                form.add_error(None, 'Incorrect membership selected')
                return self.form_invalid(form)
            else:
                self.transact(form, members, cost)
                return super().form_valid(form)

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
                form.add_error(None, 'Incorrect membership selected')
                return self.form_invalid(form)
            elif age < min_age:
                logging.debug("to young for this membership")
                form.add_error(None, 'Incorrect membership selected')
                return self.form_invalid(form)
            else:
                self.transact(form, members, level.cost)
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_authenticated:
            student = self.request.user.student_set.last()
            if student:
                self.students = student.student_family.student_set.all()
                return student.student_family is not None
        return False

    def transact(self, form, members, cost):
        uid = str(uuid.uuid4())
        membership = form.save(commit=False)
        membership.pay_status = 'start'
        membership.idempotency_key = uid
        membership.save()
        for m in members:
            membership.students.add(m)

        self.request.session['idempotency_key'] = uid
        self.request.session['line_items'] = [{'name': f'{membership.level.name} Membership',
                                              'quantity': 1, 'amount_each': cost}]
        self.request.session['payment_category'] = 'membership'
        self.request.session['payment_description'] = f'{membership.level.name} Membership'
        membership.save()
