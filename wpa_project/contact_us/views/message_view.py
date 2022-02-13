import logging
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from ..forms import MessageForm
from student_app.models import Student
from allauth.account.models import EmailAddress
logger = logging.getLogger(__name__)


class MessageView(FormView):
    template_name = 'contact_us/message.html'
    form_class = MessageForm
    success_url = reverse_lazy('registration:index')

    # def get_form(self):
    def get_initial(self):
        self.initial = super().get_initial()
        if self.request.user.is_authenticated:
            student = Student.objects.get(user=self.request.user)
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
        logging.debug(message.category.recipients.all())
        form.send_email(message)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        logging.debug(self.request.POST)
        return super().post(request, *args, **kwargs)
