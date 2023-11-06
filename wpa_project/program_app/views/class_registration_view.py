import uuid
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.base import View
import logging

from event.forms import RegistrationAdminForm
from event.models import Registration, RegistrationAdmin
from event.views.registration_view import RegistrationSuperView
from ..src import ClassRegistrationHelper
from ..tasks import wait_list_email
from src.mixin import BoardMixin
from payment.models.card import Card

logger = logging.getLogger(__name__)
Student = apps.get_model(app_label='student_app', model_name='Student')
StudentFamily = apps.get_model(app_label='student_app', model_name='StudentFamily')


class ClassRegistrationView(RegistrationSuperView):
    template_name = 'program_app/class_registration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['awrl'] = get_template('program_app/awrl.txt').render()
        context['covid_policy'] = get_template('program_app/covid_policy.txt').render()
        context['cancel_policy'] = get_template('program_app/cancellation_policy.txt').render()
        return context

    def get_form_kwargs(self):
        self.has_card = bool(Card.objects.filter(customer__user=self.request.user, enabled=True))
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        self.form = form
        processed_formset = self.process_formset()
        if not processed_formset['success']:
            return self.has_error(self.form, processed_formset['error'])
        crh = ClassRegistrationHelper()
        beginners = self.students.filter(safety_class=None).exclude(user__is_staff=True)
        returnee = self.students.exclude(safety_class=None).exclude(user__is_staff=True)
        staff = self.students.filter(user__is_staff=True)

        if not self.students.count():
            return self.has_error(form, 'No students selected')

        # check for underage students
        of_age_date = self.events[0].event_date.date().replace(year=self.events[0].event_date.date().year - 9)
        if self.students.filter(dob__gt=of_age_date).count():
            return self.has_error(form, 'Student must be at least 9 years old to participate')

        # check for overdue instructors
        if staff.filter(user__is_instructor=True, user__instructor_expire_date__lt=self.events[0].event_date).count():
            return self.has_error(form, 'Please update your instructor certification')

        # check for multiple events for non staff:
        if self.events.count() > 1 and not self.request.user.is_staff:
            return self.has_error(form, 'Must only select one class at a time.')

        event_list = []
        instructions = ''
        for event in self.events:
            # check if student signing up for incorrect class
            beginner_class = event.beginnerclass_set.last()
            event_list.append(event.id)
            if beginner_class.class_type == 'returnee' and beginners.count():
                return self.has_error(form, 'First time students cannot enroll in this class')
            elif beginner_class.class_type == 'beginner' and returnee.count():
                return self.has_error(form, 'Returning students cannot enroll in this class')

            # check if beginning student on waitlist for another class
            if event.state == 'wait':
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
            space = crh.has_space(
                self.request.user, beginner_class, beginners.count(), staff.count(), returnee.count())
            logger.warning(space)
            if space == 'full':
                crh.update_class_state(beginner_class)
                return self.has_error(form, 'Not enough space available in this class')
            elif space == 'closed':
                return self.has_error(form, 'This class is closed')
            else:
                self.wait = space == 'wait'
            # add instructions for the confirmation email
            instructions += get_template('program_app/instruction_beginner.txt').render(
                {'event': event, 'beginner_class': beginner_class}
            )

        reg_list = []
        with transaction.atomic():
            pay_status = 'start'
            if self.wait:
                if self.has_card:
                    # beginner_class.event.state = 'wait'
                    # beginner_class.event.save()
                    pay_status = 'waiting'
                    self.success_url = reverse_lazy('programs:wait_list', kwargs={'event': self.events[0].id})
                else:
                    self.success_url = reverse_lazy('payment:card_manage')
                    messages.add_message(self.request, messages.INFO,
                                         "To be placed on the wait list you need to have a card on file")
            uid = str(uuid.uuid4())
            class_date = timezone.localtime(self.events[0].event_date)
            self.request.session['idempotency_key'] = uid
            self.request.session['line_items'] = []
            self.request.session['payment_category'] = 'intro'
            self.request.session['payment_description'] = f'Class on {str(class_date)[:10]}'
            self.request.session['instructions'] = instructions

            for event in self.events:
                for f in self.formset:
                    if f.cleaned_data['register']:
                        # calling f.save() doesn't work with multiple events.
                        new_reg = Registration.objects.create(
                            event=event,
                            student=f.cleaned_data['student'],
                            pay_status=pay_status,
                            idempotency_key=uid,
                            user=self.request.user,
                            comment=f.cleaned_data.get('comment', None)
                        )
                        if new_reg.student.user and new_reg.student.user.is_staff:
                            new_reg.pay_status = 'paid'
                            self.request.session['line_items'].append({
                                'name': f"Class on {str(class_date)[:10]} staff: {new_reg.student.first_name}",
                                'quantity': 1,
                                'amount_each': 0,
                            })
                            new_reg.save()
                        else:
                            self.request.session['line_items'].append({
                                'name': f'Class on {str(class_date)[:10]} student: {new_reg.student.first_name}',
                                'quantity': 1,
                                'amount_each': event.cost_standard,
                            })
                        reg_list.append(new_reg.id)
                crh.update_class_state(event.beginnerclass_set.last())
        if self.wait and self.has_card:
            # send email to student(s) confirming they are on the wait list.
            wait_list_email.delay(reg_list)
        logger.warning(self.success_url)
        return HttpResponseRedirect(self.success_url)


class ClassRegistrationAdminView(BoardMixin, ClassRegistrationView):
    form_class = RegistrationAdminForm

    def __init__(self):
        super().__init__()
        self.admin_registration = True

    def form_valid(self, form):
        self.form = form
        if self.request.user.is_board:
            self.student_family = get_object_or_404(StudentFamily, pk=form.cleaned_data['student_family'])
        processed_formset = self.process_formset()
        if not processed_formset['success']:
            return self.has_error(self.form, processed_formset['error'])
        events = form.cleaned_data['event']

        uid = str(uuid.uuid4())
        class_date = timezone.localtime(events[0].event_date)
        if form.cleaned_data['payment']:
            self.request.session['idempotency_key'] = uid
            self.request.session['line_items'] = []
            self.request.session['payment_category'] = 'intro'
            self.request.session['payment'] = True
            self.request.session['payment_description'] = f'Class on {str(class_date)[:10]}'
        else:
            self.success_url = reverse_lazy('events:event_attend_list',
                                            kwargs={'event': events[0].id})

        pay_status = 'admin'
        for event in events:
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
            registrations = Registration.objects.filter(idempotency_key=cr.idempotency_key,
                                                        pay_status__in=['start', 'wait error'])
            logger.warning(cr.event.beginnerclass_set.last())
            if cr.pay_status == 'start':
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
                                                            kwargs={'event': cr.event.id}))
                    else:
                        return HttpResponseRedirect(reverse('payment:card_manage'))
                request.session['idempotency_key'] = str(cr.idempotency_key)
            else:
                new_idempotency_key = uuid.uuid4()
                request.session['idempotency_key'] = str(new_idempotency_key)
                registrations.update(idempotency_key=new_idempotency_key, pay_status='waiting')
                return HttpResponseRedirect(reverse('programs:wait_list',
                                                    kwargs={'event': cr.event.id}))
            request.session['line_items'] = []
            request.session['payment_category'] = 'intro'
            request.session['payment_description'] = f'Class on {str(cr.event.event_date)[:10]}'
            request.session['instructions'] = get_template('program_app/instruction_beginner.txt').render(
                {'event': cr.event, 'beginner_class': cr.event.beginnerclass_set.last()})
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
