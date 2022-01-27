from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.forms import model_to_dict
from django.shortcuts import render, get_object_or_404
import logging
from django.views.generic.base import View
from django.shortcuts import render, reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse

from ..models import Session
from ..forms import SessionForm
logger = logging.getLogger(__name__)


class SessionFormView(UserPassesTestMixin, View):
    def get(self, request, session_id=None):
        if session_id is not None:
            session = get_object_or_404(Session, pk=session_id)
            form = SessionForm(instance=session)
            class_list = session.joadclass_set.all()
            logging.debug(class_list)
        else:
            form = SessionForm()
            class_list = []

        return render(request, 'joad/session.html', {'form': form, 'object_list': class_list, 'session_id': session_id})

    def post(self, request, session_id=None):
        if session_id is not None:
            session = get_object_or_404(Session, pk=session_id)
            form = SessionForm(request.POST, instance=session)
        else:
            form = SessionForm(request.POST)

        if form.is_valid():
            f = form.save()
            return JsonResponse({'session_id': f.id, 'success': True})

        else:
            logging.debug(form.errors)
        return render(request, 'joad/session.html', {'form': form})

    def test_func(self):
        return self.request.user.is_board

