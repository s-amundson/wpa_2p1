import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from ..forms import LevelForm
from ..models import Level
from ..serializers import LevelSerializer

logger = logging.getLogger(__name__)


class LevelApiView(APIView):
    def get(self, request):
        levels = Level.objects.filter(enabled=True)
        ls = LevelSerializer(levels, many=True)
        return Response(ls.data)


class LevelView(LoginRequiredMixin, View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = Level.objects.all()

    def get(self, request, level_id=None):
        if not request.user.is_staff:
            return HttpResponseForbidden()
        if level_id is not None:
            c = get_object_or_404(Level, pk=level_id)
        else:
            c = None
        form = LevelForm(instance=c)

        return render(request, 'membership/level.html', {'form': form, 'level_id': level_id, 'table': self.table})

    def post(self, request, level_id=None):
        if level_id is not None:
            c = get_object_or_404(Level, pk=level_id)
        else:
            c = None
        form = LevelForm(request.POST, instance=c)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('membership:level'))
        else:
            logging.debug(form.errors)
            message = 'Errors on form'
        return render(request, 'membership/level.html',
                      {'form': form, 'table': self.table, 'level_id': level_id, 'message': message})
