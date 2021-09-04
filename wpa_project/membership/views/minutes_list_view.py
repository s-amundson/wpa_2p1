import logging
import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.views.generic import ListView
from django.utils import timezone, datetime_safe
from django.utils.datetime_safe import date
from django.contrib import messages
from django.forms import model_to_dict
from ..forms import MinutesForm, MinutesBusinessForm, MinutesBusinessUpdateForm, MinutesReportForm
from ..models import MinutesBusiness, Minutes, MinutesReport

logger = logging.getLogger(__name__)


class MinutesListView(LoginRequiredMixin, ListView):
    model = Minutes
    template_name = 'membership/minutes_list.html'

    def get_queryset(self):
        return Minutes.objects.all().order_by('-meeting_date')