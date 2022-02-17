import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic.base import View
from django.utils import timezone
from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages

from ..forms import BusinessForm, BusinessUpdateForm
from ..models import Business, BusinessUpdate

logger = logging.getLogger(__name__)


# class BusinessView(UserPassesTestMixin, FormView):
#     template_name = 'minutes/forms/business_form.html'
#     form_class = BusinessForm
#     success_url = reverse_lazy('registration:index')
#     form = None
#
#     def get_form(self):
#         return self.form_class(user=self.request.user, **self.get_form_kwargs())
#
#     def get_initial(self):
#         eid = self.kwargs.get("event_id", None)
#         if eid is not None:
#             event = get_object_or_404(JoadEvent, pk=eid)
#             self.initial = {'event': event}
#
#         return super().get_initial()
#
#     def form_invalid(self, form):
#         logging.debug(form.errors)
#         return super().form_invalid(form)
#
#     def form_valid(self, form):
#         self.form = form
#         students = []
#         # message = ""
#         logging.debug(form.cleaned_data)
#         event = form.cleaned_data['event']
#         if event.state != "open":
#             return self.has_error('Session in wrong state')
#
#         reg = EventRegistration.objects.filter(event=event).exclude(
#             pay_status="refunded").exclude(pay_status='canceled')
#         logging.debug(len(reg.filter(pay_status='paid')))
#
#         logging.debug(dict(self.request.POST))
#         for k, v in dict(self.request.POST).items():
#             logging.debug(k)
#             if str(k).startswith('student_') and v:
#                 i = int(str(k).split('_')[-1])
#                 s = Student.objects.get(pk=i)
#                 age = StudentHelper().calculate_age(s.dob, event.event_date)
#                 logging.debug(age)
#                 if age < 9:
#                     return self.has_error('Student is to young.')
#                 if age > 20:
#                     logging.debug(age)
#                     return self.has_error('Student is to old.')
#
#                 logging.debug(s)
#                 sreg = reg.filter(student=s)
#                 logging.debug(len(sreg))
#                 if len(sreg) == 0:
#                     students.append(s)
#                 else:
#                     return self.has_error('Student is already enrolled')
#
#         if len(students) == 0:
#             return self.has_error('Invalid student selected')
#         logging.debug(len(reg.filter(pay_status='paid')))
#         logging.debug(len(students))
#         if len(reg.filter(pay_status='paid')) + len(students) > event.student_limit:
#             return self.has_error('Class is full')
#
#         with transaction.atomic():
#             uid = str(uuid.uuid4())
#             self.request.session['idempotency_key'] = uid
#             self.request.session['line_items'] = []
#             self.request.session['payment_db'] = ['joad', 'EventRegistration']
#             self.request.session['action_url'] = reverse('programs:class_payment')
#             logging.debug(students)
#             description = f"Joad event on {str(event.event_date)[:10]} student id: "
#             for s in students:
#                 cr = EventRegistration(event=event, student=s, pay_status='start', idempotency_key=uid).save()
#                 self.request.session['line_items'].append(
#                     SquareHelper().line_item(description + f'{str(s.id)}', 1, event.cost))
#                 logging.debug(cr)
#         return HttpResponseRedirect(reverse('payment:process_payment'))
#
#     def has_error(self, message):
#         messages.add_message(self.request, messages.ERROR, message)
#         return self.form_invalid(self.form)
#         # return render(self.request, self.template_name, {'form': self.form})
#
#     def post(self, request, *args, **kwargs):
#         logging.debug(self.request.POST)
#         return super().post(request, *args, **kwargs)
#
#     def test_func(self):
#         return self.request.user.is_board

class BusinessView(LoginRequiredMixin, View):
    def get(self, request, business_id=None):
        if not request.user.is_member:
            return HttpResponseForbidden()
        if business_id:
            report = Business.objects.get(pk=business_id)
            form = BusinessForm(instance=report)
        else:
            form = BusinessForm()
        b = {'form': form, 'id': business_id}
        return render(request, 'minutes/forms/business_form.html', {'business': b})

    def post(self, request, business_id=None):
        if not request.user.is_board:
            return HttpResponseForbidden()
        logging.debug(request.POST)
        resolved = False
        if business_id:
            report = Business.objects.get(pk=business_id)
            form = BusinessForm(request.POST, instance=report)
        else:
            form = BusinessForm(request.POST)

        if form.is_valid():
            logging.debug(form.cleaned_data)
            report = form.save()
            if form.cleaned_data.get('resolved_bool', False) and report.resolved is None:
                report.resolved = timezone.now()
                resolved = True
            elif not form.cleaned_data.get('resolved_bool', False) and report.resolved:
                report.resolved = None
                resolved = False

            report.save()
            business_id = report.id
            success = True
        else:  # pragma: no cover
            logging.error(form.errors)
            success = False
        return JsonResponse({'business_id': business_id, 'success': success, 'resolved': resolved})


class BusinessUpdateView(LoginRequiredMixin, View):
    def get(self, request, update_id=None):
        logging.debug(request.GET)
        if update_id:
            report = BusinessUpdate.objects.get(pk=update_id)
            form = BusinessUpdateForm(instance=report)
        else:
            form = BusinessUpdateForm()
        b = {'form': form, 'id': update_id}
        return render(request, 'minutes/forms/business_update_form.html', {'update': b})

    def post(self, request, update_id=None):
        logging.debug(request.POST)
        if update_id:
            report = BusinessUpdate.objects.get(pk=update_id)
            form = BusinessUpdateForm(request.POST, instance=report)
        else:
            form = BusinessUpdateForm(request.POST)

        if form.is_valid():
            logging.debug(form.cleaned_data)
            report = form.save()
            update_id = report.id
            success = True
        else:  # pragma: no cover
            logging.error(form.errors)
            success = False
        return JsonResponse({'update_id': update_id, 'success': success})
