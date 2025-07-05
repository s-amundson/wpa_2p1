from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.utils import timezone

from ..forms import SendEmailForm
from ..models import User, Student
from _email.src import EmailMessage
from _email.tasks import send_bulk_email

import logging
logger = logging.getLogger(__name__)


class SendEmailView(UserPassesTestMixin, FormView):
    template_name = 'student_app/send_email.html'
    form_class = SendEmailForm
    success_url = reverse_lazy('registration:index')
    is_super = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Send Email'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_super'] = self.is_super
        return kwargs

    def form_valid(self, form):
        # send_email.delay(form.cleaned_data['recipients'], form.cleaned_data['subject'], form.cleaned_data['message'],
        #                  form.cleaned_data.get('include_days', None))
        email_users = User.objects.none()
        users = User.objects.filter(is_active=True)
        days = form.cleaned_data.get('include_days', None)
        if 'board' in form.cleaned_data['recipients']:
            email_users = email_users | users.filter(groups__name='board')
        if 'staff' in form.cleaned_data['recipients']:
            email_users = email_users | users.filter(groups__name='staff')
        if 'current members' in form.cleaned_data['recipients']:
            email_users = email_users | users.filter(groups__name='members')
            # em.bcc_from_users(, append=True)
        if 'joad' in form.cleaned_data['recipients']:
            students = Student.objects.filter(is_joad=True)
            for student in students:
                email_users = email_users | student.get_user()

        if 'students' in form.cleaned_data['recipients']:
            if days is None:
                days = 90
            d = timezone.now() - timezone.timedelta(days=days)
            students = Student.objects.filter(registration__event__event_date__gte=d, registration__attended=True)
            logger.warning(students)
            for student in students:
                email_users = email_users | student.get_user()
        logger.warning(email_users)
        if len(email_users):
            em = EmailMessage()
            em.send_mass_message(email_users, form.cleaned_data['subject'], form.cleaned_data['message'])
            send_bulk_email.delay()
            logger.warning('send delay')
        return super().form_valid(form)

    def test_func(self):
        self.is_super = self.request.user.is_superuser
        return self.request.user.has_perm('student_app.board')
