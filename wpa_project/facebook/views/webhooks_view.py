from django.views.generic import View
from django.conf import settings
from ..models import Posts
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse

import logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class PageHook(View):
    def get(self, request):
        logger.warning(self.request.GET)
        if 'hub.verify_token' in self.request.GET:
            pass
    def post(self, request):
        logger.warning(self.request.POST)
        # TODO figure out how to process data to add posts to the website as they are posted to facebook.
        return JsonResponse({})
