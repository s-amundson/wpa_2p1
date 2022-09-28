import logging
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.conf import settings

from ..forms import MessageForm
from ..models import Message
from ..tasks import send_contact_email
from student_app.models import Student
from allauth.account.models import EmailAddress
logger = logging.getLogger(__name__)


class MessageListView(UserPassesTestMixin, ListView):
    model = Message
    paginate_by = 100  # if pagination is desired
    template_name = 'contact_us/message_list.html'

    def get_queryset(self):
        queryset = super().get_queryset().exclude(spam_category='spam').order_by('-created_time')
        return queryset

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        return False


class MessageView(FormView):
    template_name = 'contact_us/message.html'
    form_class = MessageForm
    success_url = reverse_lazy('registration:index')
    message = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = settings.DEFAULT_FROM_EMAIL
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        message = self.kwargs.get("message_id", None)
        if self.request.user.is_authenticated and self.request.user.is_board and message is not None:
            self.message = get_object_or_404(Message, pk=message)
            kwargs['instance'] = self.message
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        self.initial = super().get_initial()
        if 'message_id' not in self.kwargs and self.request.user.is_authenticated:
            student = Student.objects.filter(user=self.request.user).last()
            if student is not None:
                self.initial['contact_name'] = f'{student.first_name} {student.last_name}'
                self.initial['email'] = EmailAddress.objects.get_primary(self.request.user)
        return self.initial

    def form_invalid(self, form):
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.warning(self.request.POST)
        message = form.save()
        send_contact_email.delay(message.id)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
