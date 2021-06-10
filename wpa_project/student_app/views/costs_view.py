import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic import ListView
from django.utils import timezone
# from django.db.models import model
# from django.core.exceptions import ObjectDoesNotExist

from ..forms import CostsForm
from ..models import CostsModel
from ..src import SquareHelper

logger = logging.getLogger(__name__)


class CostsView(LoginRequiredMixin, View):
    def get(self, request, cost_id=None):
        if not request.user.is_staff:
            return HttpResponseForbidden()

        form = CostsForm(initial=cost_id)

        table = CostsModel.objects.all()
        return render(request, 'student_app/form_as_p.html', {'form': form, 'table': table})

    def post(self, request, cost_id=None):
        form = CostsForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            logging.debug(form.errors)
        return render(request, 'student_app/message.html', {'message': 'payment processing error'})
