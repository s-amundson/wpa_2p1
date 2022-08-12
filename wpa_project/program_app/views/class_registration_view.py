import uuid
from django.apps import apps
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, AccessMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.base import View
from django.views.generic.edit import FormView
import logging


from ..forms import ClassRegistrationForm, ClassRegistrationAdminForm
from ..models import BeginnerClass, ClassRegistration, ClassRegistrationAdmin
from ..src import ClassRegistrationHelper
from payment.models.card import Card
from student_app.src import StudentHelper

logger = logging.getLogger(__name__)
Student = apps.get_model(app_label='student_app', model_name='Student')
StudentFamily = apps.get_model(app_label='student_app', model_name='StudentFamily')


class ClassRegistrationView(AccessMixin, FormView):
    template_name = 'program_app/class_registration.html'
    form_class = ClassRegistrationForm
    success_url = reverse_lazy('payment:make_payment')
    form = None
    students = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait = False
        self.has_card = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.student_set.last() is None or request.user.student_set.last().student_family is None:
            request.session['message'] = 'Address form is required'
            return HttpResponseRedirect(reverse('registration:profile'))
        self.has_card = bool(Card.objects.filter(customer__user=self.request.user, enabled=True))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['this_month'] = timezone.localtime(timezone.now()).month
        context['family'] = self.request.user.student_set.last().student_family
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # logging.debug(kwargs)
        if self.kwargs.get('beginner_class', None) is not None:
            kwargs['initial']['beginner_class'] = self.kwargs.get('beginner_class')
        # logging.debug(kwargs)
        return kwargs

    def get_form(self):
        try:
            self.students = Student.objects.get(user=self.request.user).student_family.student_set.all()
        except (Student.DoesNotExist, AttributeError):  # pragma: no cover
            self.request.session['message'] = 'Address form is required'
            return HttpResponseRedirect(reverse('registration:profile'))
        return self.form_class(self.students, self.request.user, **self.get_form_kwargs())

    def form_invalid(self, form):
        logging.debug(self.request.POST)
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        self.form = form

        beginner_class = BeginnerClass.objects.get(pk=self.form.cleaned_data['beginner_class'])
        beginner = 0
        returnee = 0
        instructor = 0
        students = []
        instructors = []
        logging.debug(self.form.cleaned_data)
        for k, v in self.form.cleaned_data.items():
            if str(k).startswith('student_') and v:
                i = int(str(k).split('_')[-1])
                s = Student.objects.get(pk=i)

                # logging.debug(s)
                if StudentHelper().calculate_age(s.dob, beginner_class.class_date) < 9:
                    return self.has_error('Student must be at least 9 years old to participate')

                if s.user is not None and s.user.is_staff:
                    logging.debug('student is staff')
                    if s.user.is_instructor:
                        # logging.debug(s.user.instructor_expire_date)
                        if s.user.instructor_expire_date is None \
                                or s.user.instructor_expire_date < timezone.localdate(timezone.now()):
                            return self.has_error('Please update your instructor certification')

                    if len(ClassRegistration.objects.filter(
                            beginner_class=beginner_class, student=s).exclude(
                            pay_status__in=['canceled', "refunded", 'refund donated'])) == 0:
                        instructor += 1
                        instructors.append(s)
                    else:
                        return self.has_error(f'{s.first_name} is already enrolled')

                else:
                    reg = ClassRegistration.objects.filter(student=s).exclude(
                        pay_status__in=['canceled', "refunded", 'refund donated'])
                    if len(reg.filter(beginner_class=beginner_class)) == 0:
                        if s.safety_class is None:
                            # logging.debug(len(reg))
                            if len(reg.filter(beginner_class__class_date__gt=timezone.localdate(timezone.now()))) > 0:
                                return self.has_error(f'{s.first_name} is enrolled in another beginner class')
                            else:
                                beginner += 1
                                students.append(s)
                        else:
                            returnee += 1
                            students.append(s)
                    else:
                        return self.has_error('Student is already enrolled')

        if 0 == beginner + returnee + instructor:
            return self.has_error('No students selected')

        self.request.session['class_registration'] = {'beginner_class': beginner_class.id, 'beginner': beginner,
                                                      'returnee': returnee}
        space = ClassRegistrationHelper().has_space(self.request.user, beginner_class, beginner, instructor, returnee)
        if space == 'full':
            return self.has_error('Not enough space available in this class')
        else:
            self.wait = space == 'wait'
            return self.transact(beginner_class, students, instructors)
        # enrolled_count = ClassRegistrationHelper().enrolled_count(beginner_class)
        # logging.debug(enrolled_count)
        # logging.debug(beginner)
        # if beginner_class.state in ['open', 'wait']:  # in case it changed since user got the self.form.
        #     if beginner and enrolled_count['beginner'] + beginner > beginner_class.beginner_limit:
        #         if beginner and enrolled_count['beginner'] + beginner > beginner_class.beginner_limit + \
        #                 beginner_class.beginner_wait_limit:
        #             return self.has_error('Not enough space available in this class')
        #         if enrolled_count['beginner'] + beginner > beginner_class.beginner_limit:
        #             self.wait = True
        #
        #     if returnee and enrolled_count['returnee'] + returnee > beginner_class.returnee_limit:
        #         if returnee and enrolled_count['returnee'] + returnee > beginner_class.returnee_limit + \
        #                 beginner_class.returneewait_limit:
        #             return self.has_error('Not enough space available in this class')
        #         if enrolled_count['returnee'] + returnee > beginner_class.returnee_limit:
        #             self.wait = True
        #
        #     if instructor and enrolled_count['staff'] + instructor > beginner_class.instructor_limit:
        #         return self.has_error('Not enough space available in this class')
        #
        #     return self.transact(beginner_class, students, instructors)
        #
        # elif beginner_class.state in ['full', 'closed'] and self.request.user.is_staff:
        #     if instructor and enrolled_count['staff'] + instructor > beginner_class.instructor_limit:
        #         return self.has_error('Not enough space available in this class')
        #     else:
        #         return self.transact(beginner_class, students, instructors)

    def has_error(self, message):
        logging.debug(message)
        messages.add_message(self.request, messages.ERROR, message)
        return self.form_invalid(self.form)

    def transact(self, beginner_class, students, instructors):
        with transaction.atomic():
            pay_status = 'start'
            logging.debug(self.wait)
            if self.wait:
                logging.debug(self.has_card)
                if self.has_card:
                    beginner_class.state = 'wait'
                    beginner_class.save()
                    pay_status = 'waiting'
                    self.success_url = reverse_lazy('programs:wait_list', kwargs={'beginner_class': beginner_class.id})
                else:
                    self.success_url = reverse_lazy('payment:card_manage')
                    messages.add_message(self.request, messages.INFO,
                                         "To be placed on the wait list you need to have a card on file")
            uid = str(uuid.uuid4())
            self.request.session['idempotency_key'] = uid
            self.request.session['line_items'] = []
            self.request.session['payment_category'] = 'intro'
            self.request.session['payment_description'] = f'Class on {str(beginner_class.class_date)[:10]}'
            # logging.debug(students)
            for s in students:
                if s.safety_class is None:
                    n = True
                else:
                    n = False
                cr = ClassRegistration.objects.create(beginner_class=beginner_class, student=s, new_student=n,
                                       pay_status=pay_status, idempotency_key=uid, user=self.request.user)
                self.request.session['line_items'].append({
                    'name': f'Class on {str(beginner_class.class_date)[:10]} student: {s.first_name}',
                    'quantity': 1,
                    'amount_each': beginner_class.cost,
                     }
                )
                # logging.debug(cr)
            for i in instructors:
                cr = ClassRegistration.objects.create(beginner_class=beginner_class, student=i, new_student=False,
                                       pay_status='paid', idempotency_key=uid, user=self.request.user)
                self.request.session['line_items'].append({
                    'name': f"Class on {str(beginner_class.class_date)[:10]} instructor: {i.first_name}",
                    'quantity': 1,
                    'amount_each': 0,
                     }
                )

        return HttpResponseRedirect(self.success_url)


class ClassRegistrationAdminView(UserPassesTestMixin, ClassRegistrationView):
    template_name = 'student_app/form_as_p.html'
    form = None
    form_class = ClassRegistrationAdminForm
    students = None

    def get_form(self):
        # logging.debug('get_form')
        return self.form_class(self.students, self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        self.form = form
        logging.debug(form.cleaned_data)
        beginner_class = BeginnerClass.objects.get(pk=form.cleaned_data['beginner_class'])
        # logging.debug(beginner_class.cost)

        uid = str(uuid.uuid4())
        if form.cleaned_data['payment']:
            self.request.session['idempotency_key'] = uid
            self.request.session['line_items'] = []
            self.request.session['payment_category'] = 'intro'
            self.request.session['payment'] = True
            self.request.session['payment_description'] = f'Class on {str(beginner_class.class_date)[:10]}'
        else:
            self.success_url = reverse_lazy('programs:class_attend_list',
                                            kwargs={'beginner_class': form.cleaned_data['beginner_class']})

        cr = ClassRegistration.objects.filter(beginner_class=beginner_class)
        # logging.debug(timezone.now())
        for k, v in form.cleaned_data.items():
            if str(k).startswith('student_') and v:
                i = int(str(k).split('_')[-1])
                s = Student.objects.get(pk=i)

                if s.safety_class is None:
                    n = True
                else:
                    n = False

                if len(cr.filter(student=s, pay_status='admin')) > 0:
                    return self.has_error(f'{s.first_name} {s.last_name} already registered by admin')
                elif len(cr.filter(student=s, pay_status='paid')) > 0:
                    return self.has_error(f'{s.first_name} {s.last_name} already registered')
                else:
                    pay_status = 'admin'
                    if form.cleaned_data['payment']:
                        pay_status = 'start'
                        self.request.session['line_items'].append({
                            'name': f'Class on {str(beginner_class.class_date)[:10]} student: {s.first_name}',
                            'quantity': 1,
                            'amount_each': beginner_class.cost,
                             }
                        )
                    ncr = ClassRegistration.objects.create(beginner_class=beginner_class, student=s, new_student=n,
                                                           pay_status=pay_status, idempotency_key=uid,
                                                           user=form.cleaned_data['student'].user, reg_time=timezone.now())
                    note = form.cleaned_data['notes']
                    ClassRegistrationAdmin.objects.create(class_registration=ncr, staff=self.request.user, note=note)

        return HttpResponseRedirect(self.success_url)

    def test_func(self):
        fid = self.kwargs.get('family_id', None)
        if fid is not None:
            student_family = get_object_or_404(StudentFamily, pk=fid)
            self.students = student_family.student_set.all()
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        else:
            return False


class ResumeRegistrationView(LoginRequiredMixin, View):
    def get(self, request, reg_id=None):
        try:
            students = Student.objects.get(user=request.user).student_family.student_set.all()
        except (Student.DoesNotExist, AttributeError):  # pragma: no cover
            request.session['message'] = 'Address form is required'
            return HttpResponseRedirect(reverse('registration:profile'))

        if reg_id:  # to regain an interrupted payment
            cr = get_object_or_404(ClassRegistration, pk=reg_id)
            # logging.debug(f'Students: {students[0].student_family.id}, cr:{cr.student.student_family.id}')
            if cr.student.student_family != students[0].student_family:  # pragma: no cover
                return Http404("registration mismatch")
            registrations = ClassRegistration.objects.filter(idempotency_key=cr.idempotency_key)
            space = ClassRegistrationHelper().has_space(self.request.user,
                                                        cr.beginner_class,
                                                        len(registrations.filter(student__safety_class__isnull=True)),
                                                        0,
                                                        len(registrations.filter(student__safety_class__isnull=False))
                                                        )
            logging.debug(space)
            if space == 'full':
                messages.add_message(self.request, messages.ERROR, 'Not enough space available in this class')
                return HttpResponseRedirect(reverse('programs:calendar'))
            elif space == 'wait':
                if Card.objects.filter(customer__user=self.request.user, enabled=True):
                    registrations.update(pay_status='waiting')
                    return HttpResponseRedirect(reverse('programs:wait_list',
                                                        kwargs={'beginner_class': cr.beginner_class.id}))
                else:
                    return HttpResponseRedirect(reverse('payment:card_manage'))

            request.session['idempotency_key'] = str(cr.idempotency_key)
            request.session['line_items'] = []
            request.session['payment_category'] = 'intro'
            request.session['payment_description'] = f'Class on {str(cr.beginner_class.class_date)[:10]}'
            beginner = 0
            returnee = 0

            for r in registrations:
                request.session['line_items'].append({
                        'name': f'Class on {str(r.beginner_class.class_date)[:10]} student: {r.student.first_name}',
                        'quantity': 1,
                        'amount_each': r.beginner_class.cost,
                    }
                )
                if r.student.safety_class is None:
                    beginner += 1
                else:
                    returnee += 1

            request.session['class_registration'] = {'beginner_class': r.beginner_class.id, 'beginner': beginner,
                                                     'returnee': returnee}
            return HttpResponseRedirect(reverse('payment:make_payment'))
