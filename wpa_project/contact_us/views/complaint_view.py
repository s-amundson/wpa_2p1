import logging
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.forms import modelformset_factory
from django.template.loader import get_template
from django.conf import settings
from allauth.account.models import EmailAddress

from ..forms import ComplaintForm, ComplientCommentForm
from ..models import Complaint, ComplaintComment
from ..tasks import send_contact_email
from student_app.models import User
from allauth.account.models import EmailAddress
from src.mixin import BoardMixin
from _email.src.email import EmailMessage
logger = logging.getLogger(__name__)


class ComplaintListView(BoardMixin, ListView):
    model = Complaint
    paginate_by = 20  # if pagination is desired
    template_name = 'contact_us/complaint_list.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['spam_list'] = self.kwargs.get('spam', False)
    #     return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_time')


class ComplaintView(UserPassesTestMixin, FormView):
    template_name = 'contact_us/complaint.html'
    form_class = ComplaintForm
    success_url = reverse_lazy('registration:index')
    complaint = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.get_formset()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'pk' in self.kwargs:
            kwargs['instance'] = self.complaint = get_object_or_404(Complaint, pk=self.kwargs.get('pk'))
        # message = self.kwargs.get("pk", None)
    #     if self.request.user.is_authenticated and self.request.user.is_board and message is not None:
    #         self.message = get_object_or_404(Message, pk=message)
    #         kwargs['instance'] = self.message
    #     kwargs['user'] = self.request.user
        return kwargs

    def get_formset(self, **kwargs):
        formset = modelformset_factory(ComplaintComment, form=ComplientCommentForm, can_delete=False, extra=1)
        data = None
        if self.request.method.lower() == 'post':
            data = self.request.POST
        formset = formset(
            queryset=ComplaintComment.objects.filter(complaint=self.complaint).order_by('comment_date'),
            initial=[{'complaint': self.complaint}], data=data, **kwargs
            )
        return formset

    def form_invalid(self, form):  # pragma: no cover
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        if self.complaint is not None:
            formset = self.get_formset()
            # logger.warning(formset.cleaned_data)
            if formset.is_valid():
                formset.save()

            else:  # pragma: no cover
                logger.warning(formset.errors)
                logger.warning(formset.non_form_errors())
        # logger.warning(self.complaint.id)
        complaint = form.save()
        if not form.cleaned_data.get('anonymous', True):
            complaint.user = self.request.user
        if self.complaint is None:
            logger.warning('send email')
            complaint_dict = {'complaint': complaint, 'student': None, 'email': None}
            logger.warning(complaint.user)
            if complaint.user is not None:
                complaint_dict['student'] = complaint.user.student_set.last()
                complaint_dict['email'] = EmailAddress.objects.get_primary(complaint.user)

            EmailMessage().send_mass_bcc(
                User.objects.filter(is_board=True),
                'WPA Complaint Filed',
                get_template('contact_us/email/complaint.txt').render(complaint_dict),
                get_template('contact_us/email/complaint.html').render(complaint_dict)
            )

        if complaint.resolved_date is None and form.cleaned_data.get('resolved', False):
            complaint.resolved_date = timezone.now()
        complaint.save()
        self.success_url = reverse_lazy('contact_us:thanks')
        return super().form_valid(form)
    #
    # def post(self, request, *args, **kwargs):
    #     return super().post(request, *args, **kwargs)

    def test_func(self):
        if self.request.user.is_authenticated:
            if 'pk' in self.kwargs:
                self.complaint = get_object_or_404(Complaint, pk=self.kwargs.get('pk'))
                return self.request.user.is_board
            return True
        return False
