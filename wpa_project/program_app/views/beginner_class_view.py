import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from django.utils import timezone
from django.contrib import messages
from django.forms import model_to_dict

from ..forms import BeginnerClassForm, SendClassEmailForm
from ..models import BeginnerClass, ClassRegistration
from ..src import ClassRegistrationHelper
from ..tasks import refund_class
from event.models import Event
from payment.models import CostsModel

logger = logging.getLogger(__name__)


class BeginnerClassView(UserPassesTestMixin, FormView):
    template_name = 'program_app/beginner_class.html'
    form_class = BeginnerClassForm
    success_url = reverse_lazy('programs:class_list')
    beginner_class = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email_form'] = SendClassEmailForm(beginner_class=self.beginner_class)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.beginner_class is not None:
            kwargs['instance'] = self.beginner_class
        else:
            try:
                c = BeginnerClass.objects.latest('event__event_date').event.event_date
                c = c + timedelta(days=7)
            except (BeginnerClass.DoesNotExist, AttributeError):  # pragma: no cover
                c = timezone.now()
            try:
                cost = CostsModel.objects.filter(name='Beginner Class', enabled=True)[:1] #[0].standard_cost
                costs = cost[0].standard_cost
            except (CostsModel.DoesNotExist, IndexError) as e:  # pragma: no cover
                costs = 0
                messages.add_message(self.request, messages.ERROR, 'cost does not exist')
                logging.error('cost does not exist')
            kwargs['initial'] = {'class_date': c, 'beginner_limit': 20, 'returnee_limit': 20, 'state': 'scheduled',
                                 'cost': costs}
        return kwargs

    def form_invalid(self, form):
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        # don't add a class on a date that already has a class.
        # logging.warning(form.cleaned_data)
        if len(BeginnerClass.objects.filter(event__event_date=form.cleaned_data['class_date'])) > 0 \
                and self.beginner_class is None:
            # logging.debug('Class Exists')
            messages.add_message(self.request, messages.ERROR, 'A class at this time already exists')
            return self.form_invalid(form)
        if self.beginner_class:
            self.beginner_class.event.event_date = form.cleaned_data['class_date']
            self.beginner_class.event.cost_standard = form.cleaned_data['cost']
            self.beginner_class.event.cost_member = form.cleaned_data['cost']
            self.beginner_class.event.state = form.cleaned_data['state']
            self.beginner_class.event.type = 'class'
            self.beginner_class.event.save()
            event = self.beginner_class.event
        else:
            event = Event.objects.create(
                event_date=form.cleaned_data['class_date'],
                cost_standard=form.cleaned_data['cost'],
                cost_member=form.cleaned_data['cost'],
                state=form.cleaned_data['state'],
                type='class'
            )
        bc = form.save()
        bc.event = event
        bc.save()

        # logging.debug(bc.class_type)
        if bc.class_type == 'beginner' and bc.returnee_limit > 0:
            messages.add_message(self.request, messages.WARNING,
                                 "beginner class can't have a returnee limit greater then 0")
            bc.returnee_limit = 0
            bc.save()
        elif bc.class_type == 'returnee' and bc.beginner_limit > 0:
            messages.add_message(self.request, messages.WARNING,
                                 "returning class can't have a beginner limit greater then 0")
            bc.beginner_limit = 0
            bc.save()
        if bc.event.state == 'canceled':
            refund_class.delay(bc.id, form.cleaned_data['cancel_message'])
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_authenticated:
            bid = self.kwargs.get('beginner_class', None)
            if bid is not None:
                self.beginner_class = get_object_or_404(BeginnerClass, pk=bid)
                logging.warning(self.beginner_class.event)
                logging.warning(self.beginner_class.event.event_date)
                logging.warning(timezone.localtime(self.beginner_class.event.event_date))
                self.success_url = reverse_lazy('programs:class_attend_list', kwargs={'beginner_class': bid})
            return self.request.user.is_board
        else:
            return False


class BeginnerClassListView(LoginRequiredMixin, ListView):
    template_name = 'program_app/beginner_class_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['past'] = self.kwargs.get('past', False)
        return context

    def get_queryset(self):
        crh = ClassRegistrationHelper()
        if self.kwargs.get('past', False):
            bc = BeginnerClass.objects.filter(
                event__event_date__lte=timezone.localtime(timezone.now()).date()).order_by('-event__event_date')
        else:
            bc = BeginnerClass.objects.filter(
                event__event_date__gte=timezone.localtime(timezone.now()).date()).order_by('event__event_date')
        queryset = []
        for c in bc:
            d = model_to_dict(c)
            d['event_date'] = c.event.event_date
            d = {**d, **crh.enrolled_count(c)}
            queryset.append(d)
        # logging.debug(len(queryset))
        return queryset
