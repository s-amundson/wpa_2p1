import logging
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.conf import settings

from ..forms import MessageForm
from ..models import Message
from student_app.models import Student
from allauth.account.models import EmailAddress
logger = logging.getLogger(__name__)


class MessageListView(UserPassesTestMixin, ListView):
    model = Message
    paginate_by = 100  # if pagination is desired
    template_name = 'contact_us/message_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.order_by('-id')
        return queryset

    def test_func(self):
        return self.request.user.is_board


class MessageView(FormView):
    template_name = 'contact_us/message.html'
    form_class = MessageForm
    success_url = reverse_lazy('registration:index')
    message = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = settings.DEFAULT_FROM_EMAIL
        return context

    def get_form(self):
        message = self.kwargs.get("message_id", None)
        if self.request.user.is_authenticated and self.request.user.is_board and message is not None:
            self.message = get_object_or_404(Message, pk=message)
            return self.form_class(instance=self.message, **self.get_form_kwargs())
        return self.form_class(**self.get_form_kwargs())

    def get_initial(self):
        self.initial = super().get_initial()
        if self.request.user.is_authenticated:
            student = Student.objects.filter(user=self.request.user).last()
            if student is not None:
                self.initial['contact_name'] = f'{student.first_name} {student.last_name}'
                self.initial['email'] = EmailAddress.objects.get_primary(self.request.user)
        return self.initial

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        message = form.save()
        form.send_email(message)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
