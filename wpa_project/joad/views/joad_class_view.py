from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import model_to_dict
from django.shortcuts import render, get_object_or_404
import logging
from django.views.generic.base import View
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.views.generic.list import ListView

from ..models import JoadClass
from ..forms import ClassForm

logger = logging.getLogger(__name__)


class JoadClassView(UserPassesTestMixin, View):
    def get(self, request, class_id=None):
        if class_id:
            jc = get_object_or_404(JoadClass, pk=class_id)
            form = ClassForm(instance=jc)
        else:
            form = ClassForm()
        return render(request, 'joad/forms/class_form.html', {'form': form})

    def post(self, request, class_id=None):
        logging.debug(request.POST)
        if class_id:
            jc = get_object_or_404(JoadClass, pk=class_id)
            form = ClassForm(request.POST, instance=jc)
        else:
            form = ClassForm(request.POST)
        if form.is_valid():
            f = form.save()
            return JsonResponse({'id': f.id, 'class_date': f.class_date, 'state': f.state, 'success': True})

    def test_func(self):
        return self.request.user.is_board


class ClassListView(LoginRequiredMixin, ListView):
    model = JoadClass
    template_name = 'joad/tables/class_table.html'
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context

    def get_queryset(self):
        sid = self.kwargs.get("session_id", None)
        logging.debug(sid)
        if sid == 0:
            object_list = self.model.objects.filter(session__state="open")
        elif sid is not None:
            object_list = self.model.objects.filter(session_id=sid).order_by('class_date')
        else:
            object_list = []

        return object_list

