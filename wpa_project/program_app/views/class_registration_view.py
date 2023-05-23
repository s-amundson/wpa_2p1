import uuid
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.base import View
import logging

from event.forms import RegistrationAdminForm
from event.models import Registration, RegistrationAdmin
from event.views.registration_view import RegistrationSuperView
from ..src import ClassRegistrationHelper
from src.mixin import BoardMixin
from payment.models.card import Card

logger = logging.getLogger(__name__)
Student = apps.get_model(app_label='student_app', model_name='Student')
StudentFamily = apps.get_model(app_label='student_app', model_name='StudentFamily')


class ClassRegistrationView(RegistrationSuperView):
    template_name = 'program_app/class_registration.html'

    def get_form_kwargs(self):
        self.has_card = bool(Card.objects.filter(customer__user=self.request.user, enabled=True))
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        self.form = form
        processed_formset = self.process_formset()
        if not processed_formset['success']:
            return self.has_error(self.form, processed_formset['error'])

        beginners = self.students.filter(safety_class=None)
        returnee = self.students.exclude(safety_class=None).exclude(user__is_staff=True)
        staff = self.students.filter(user__is_staff=True)

        if not self.students.count():
            return self.has_error(form, 'No students selected')

        # check for underage students
        of_age_date = self.event.event_date.date().replace(year=self.event.event_date.date().year - 9)
        logger.warning(of_age_date)
        if self.students.filter(dob__gt=of_age_date).count():
            return self.has_error(form, 'Student must be at least 9 years old to participate')

        # check for overdue instructors
        if staff.filter(user__is_instructor=True, user__instructor_expire_date__lt=self.event.event_date).count():
            return self.has_error(form, 'Please update your instructor certification')

        # check if student signing up for incorrect class
        beginner_class = self.event.beginnerclass_set.last()
        if beginner_class.class_type == 'returnee' and beginners.count():
            return self.has_error(form, 'First time students cannot enroll in this class')
        elif beginner_class.class_type == 'beginner' and returnee.count():
            return self.has_error(form, 'Returning students cannot enroll in this class')

        # check if beginning student on waitlist for another class
        if self.event.state == 'wait':
            for s in beginners:
                reg = Registration.objects.filter(
                    student=s,
                    event__type='class',
                    event__event_date__gt=timezone.now(),
                    pay_status='waiting'
                ).exclude(
                    pay_status__in=['canceled', "refunded", 'refund', 'refund donated'],
                )
                if reg.count():
                    return self.has_error(form, f'{s.first_name} is on wait list for another beginner class')

        # check if class is full
        space = ClassRegistrationHelper().has_space(
            self.request.user, beginner_class, beginners.count(), staff.count(), returnee.count())
        logger.warning(space)
        if space == 'full':
            return self.has_error(form, 'Not enough space available in this class')
        elif space == 'closed':
            return self.has_error(form, 'This class is closed')
        else:
            self.wait = space == 'wait'

        with transaction.atomic():
            pay_status = 'start'
            logger.debug(self.wait)
            if self.wait:
                logger.debug(self.has_card)
                if self.has_card:
                    # beginner_class.event.state = 'wait'
                    # beginner_class.event.save()
                    pay_status = 'waiting'
                    self.success_url = reverse_lazy('programs:wait_list', kwargs={'beginner_class': beginner_class.id})
                else:
                    self.success_url = reverse_lazy('payment:card_manage')
                    messages.add_message(self.request, messages.INFO,
                                         "To be placed on the wait list you need to have a card on file")
            uid = str(uuid.uuid4())
            class_date = timezone.localtime(self.event.event_date)
            self.request.session['idempotency_key'] = uid
            self.request.session['line_items'] = []
            self.request.session['payment_category'] = 'intro'
            self.request.session['payment_description'] = f'Class on {str(class_date)[:10]}'
            # logger.debug(students)
            for s in self.students.exclude(user__is_staff=True):

                cr = Registration.objects.create(event=self.event, student=s,
                                       pay_status=pay_status, idempotency_key=uid, user=self.request.user)
                self.request.session['line_items'].append({
                    'name': f'Class on {str(class_date)[:10]} student: {s.first_name}',
                    'quantity': 1,
                    'amount_each': self.event.cost_standard,
                     }
                )
                # logger.debug(cr)
            for i in self.students.filter(user__is_staff=True):
                cr = Registration.objects.create(event=beginner_class.event, student=i,
                                       pay_status='paid', idempotency_key=uid, user=self.request.user)
                self.request.session['line_items'].append({
                    'name': f"Class on {str(class_date)[:10]} staff: {i.first_name}",
                    'quantity': 1,
                    'amount_each': 0,
                     }
                )
        if self.wait:
            ClassRegistrationHelper().update_class_state(beginner_class)
        return HttpResponseRedirect(self.success_url)


class ClassRegistrationAdminView(BoardMixin, ClassRegistrationView):
    form_class = RegistrationAdminForm

    def __init__(self):
        super().__init__()
        self.admin_registration = True

    def form_valid(self, form):
        self.form = form
        processed_formset = self.process_formset()
        if not processed_formset['success']:
            return self.has_error(self.form, processed_formset['error'])
        event = form.cleaned_data['event']

        uid = str(uuid.uuid4())
        class_date = timezone.localtime(event.event_date)
        if form.cleaned_data['payment']:
            self.request.session['idempotency_key'] = uid
            self.request.session['line_items'] = []
            self.request.session['payment_category'] = 'intro'
            self.request.session['payment'] = True
            self.request.session['payment_description'] = f'Class on {str(class_date)[:10]}'
        else:
            self.success_url = reverse_lazy('events:event_attend_list',
                                            kwargs={'event': event.id})

        pay_status = 'admin'
        for s in self.students:
            if form.cleaned_data['payment']:
                pay_status = 'start'
                self.request.session['line_items'].append({
                    'name': f'Class on {str(class_date)[:10]} student: {s.first_name}',
                    'quantity': 1,
                    'amount_each': event.cost_standard,
                    }
                )
            ncr = Registration.objects.create(
                event=event,
                student=s,
                pay_status=pay_status,
                idempotency_key=uid,
                user=form.cleaned_data['student'].user,
                reg_time=timezone.now())

            note = form.cleaned_data['notes']
            RegistrationAdmin.objects.create(class_registration=ncr, staff=self.request.user, note=note)

        return HttpResponseRedirect(self.success_url)


class ResumeRegistrationView(LoginRequiredMixin, View):
    def get(self, request, reg_id=None):
        try:
            students = Student.objects.get(user=request.user).student_family.student_set.all()
        except (Student.DoesNotExist, AttributeError):  # pragma: no cover
            request.session['message'] = 'Address form is required'
            return HttpResponseRedirect(reverse('registration:profile'))

        if reg_id:  # to regain an interrupted payment
            cr = get_object_or_404(Registration, pk=reg_id)
            # logger.debug(f'Students: {students[0].student_family.id}, cr:{cr.student.student_family.id}')
            if cr.student.student_family != students[0].student_family:  # pragma: no cover
                return Http404("registration mismatch")
            registrations = Registration.objects.filter(idempotency_key=cr.idempotency_key)
            logger.warning(cr.event.beginnerclass_set.last())
            space = ClassRegistrationHelper().has_space(self.request.user,
                                                        cr.event.beginnerclass_set.last(),
                                                        len(registrations.filter(student__safety_class__isnull=True)),
                                                        0,
                                                        len(registrations.filter(student__safety_class__isnull=False))
                                                        )
            logger.debug(space)
            if space == 'full':
                messages.add_message(self.request, messages.ERROR, 'Not enough space available in this class')
                return HttpResponseRedirect(reverse('programs:calendar'))
            elif space == 'wait':
                if Card.objects.filter(customer__user=self.request.user, enabled=True):
                    registrations.update(pay_status='waiting')
                    return HttpResponseRedirect(reverse('programs:wait_list',
                                                        kwargs={'beginner_class': cr.event.beginnerclass_set.last().id}))
                else:
                    return HttpResponseRedirect(reverse('payment:card_manage'))

            request.session['idempotency_key'] = str(cr.idempotency_key)
            request.session['line_items'] = []
            request.session['payment_category'] = 'intro'
            request.session['payment_description'] = f'Class on {str(cr.event.event_date)[:10]}'
            beginner = 0
            returnee = 0

            for r in registrations:
                class_date = timezone.localtime(r.event.event_date)
                request.session['line_items'].append({
                        'name': f'Class on {str(class_date)[:10]} student: {r.student.first_name}',
                        'quantity': 1,
                        'amount_each': r.event.cost_standard,
                    }

                )
                if r.student.safety_class is None:
                    beginner += 1
                else:
                    returnee += 1

            request.session['class_registration'] = {
                'beginner_class': r.event.beginnerclass_set.last().id,
                'beginner': beginner,
                'returnee': returnee
            }
            return HttpResponseRedirect(reverse('payment:make_payment'))
