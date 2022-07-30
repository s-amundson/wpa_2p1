import logging
import csv
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.list import ListView
from django.utils import timezone
from django.http import HttpResponse
from ..forms import MemberExpireDateForm
from ..models import Member
logger = logging.getLogger(__name__)


class MemberList(UserPassesTestMixin, ListView):
    model = Member
    paginate_by = 100  # if pagination is desired
    form_class = MemberExpireDateForm
    initial_date = timezone.datetime.today()
    csv_response = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logging.debug(self.request.GET)
        logging.debug(bool(self.request.GET))
        if self.request.GET:
            context['form'] = self.form_class(self.request.GET)
        else:
            context['form'] = self.form_class(initial={'query_date': self.initial_date})
        return context

    def get_queryset(self):
        form = self.form_class(self.request.GET)
        object_list = self.model.objects.filter(expire_date__gte=timezone.datetime.today()).order_by('student__last_name')
        if form.is_valid():
            logging.debug(form.cleaned_data)
            if form.cleaned_data['query_date']:
                d = form.cleaned_data['query_date']
                self.initial_date = d
                logging.debug(d)
                object_list = self.model.objects.filter(expire_date__gte=d).filter(begin_date__lte=d)
                if form.cleaned_data['order_by'] == 'first':
                    object_list = object_list.order_by('student__first_name')
                elif form.cleaned_data['order_by'] == 'expire':
                    object_list = object_list.order_by('expire_date')
                else:
                    object_list = object_list.order_by('student__last_name')
            if form.cleaned_data['csv_export']:
                self.csv_response = True
        else:
            logging.debug(form.errors)
        return object_list

    def render_to_response(self, context, **response_kwargs):
        if self.csv_response:
            output = []
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            # Header
            writer.writerow(['First Name', 'Last Name', 'Expire Date'])
            for member in self.object_list:
                output.append([member.student.first_name, member.student.last_name, member.expire_date])
            # CSV Data
            writer.writerows(output)
            return response
        else:
            return super().render_to_response(context, **response_kwargs)

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        else:
            return False
