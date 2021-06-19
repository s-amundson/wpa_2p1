from django.contrib.auth.mixins import LoginRequiredMixin

import logging

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from ..serializers import ThemeSerializer

logger = logging.getLogger(__name__)


class ThemeView(LoginRequiredMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        serializer = ThemeSerializer(data=request.data)

        if serializer.is_valid():
            logging.debug('valid')
            logging.debug(serializer.validated_data)
            # u = User.objects.get(request.user)
            request.user.dark_theme = serializer.validated_data['theme']
            request.user.save()
            return Response(serializer.data)

        else:
            logging.debug(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
