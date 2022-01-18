from django.contrib.auth.mixins import UserPassesTestMixin
from django.forms import model_to_dict
from django.shortcuts import render, get_object_or_404
import logging
from django.views.generic.base import View
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse

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
