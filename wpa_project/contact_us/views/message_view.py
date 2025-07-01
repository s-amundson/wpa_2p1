import logging
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from ipware import get_client_ip

from ..forms import MessageForm
from ..models import Category, Message
from ..tasks import send_contact_email
from student_app.models import Student
from allauth.account.models import EmailAddress
logger = logging.getLogger(__name__)


class MessageListView(UserPassesTestMixin, ListView):
    model = Message
    paginate_by = 20  # if pagination is desired
    template_name = 'contact_us/message_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['spam_list'] = self.kwargs.get('spam', False)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.kwargs.get('spam', False):
            queryset = queryset.filter(spam_category='spam')
        else:
            queryset = queryset.exclude(spam_category='spam')
        return queryset.order_by('-created_time')

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.has_perm('student_app:board')
        return False


class MessageView(FormView):
    template_name = 'contact_us/message.html'
    form_class = MessageForm
    success_url = reverse_lazy('registration:index')
    message = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.request.session.pop('recaptcha_score')
        if self.request.user.is_authenticated:
            context['probably_human'] = True
        else:
            score = self.request.session.get('recaptcha_score', 0)
            logging.warning(score)
            context['probably_human'] = score > 0.5
        # cat = Category.objects.filter(title='Website').last()
        # if cat is not None:
        #     context['email'] = cat.email
        # else:
        #     context['email'] = settings.DEFAULT_FROM_EMAIL
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        message = self.kwargs.get("message_id", None)
        if self.request.user.is_authenticated and self.request.user.has_perm('user.board') and message is not None:
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
        def make_error():
            form.add_error(None, 'In order to prevent spam we are unable to process request at this time.')
            form.can_submit = False
            self.request.session['contact_us'] = timezone.now().isoformat()
            return self.form_invalid(form)

        if self.request.user.is_authenticated and self.request.user.is_board:
            pass
        else:
            # check users history
            recent_time = timezone.now() - timezone.timedelta(hours=2)
            if 'contact_us' in self.request.session:
                if timezone.datetime.fromisoformat(self.request.session['contact_us']) > recent_time:
                    return make_error()
            recent = Message.objects.filter(created_time__gt=recent_time, email=form.cleaned_data['email'])
            if recent:
                return make_error()

        # save record
        self.request.session['contact_us'] = timezone.now().isoformat()
        message = form.save()
        client_ip, is_routable = get_client_ip(self.request)
        send_contact_email.delay(message.id, client_ip)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
