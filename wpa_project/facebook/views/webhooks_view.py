from django.views.generic import View
from django.conf import settings
from ..models import Posts

import logging
logger = logging.getLogger(__name__)


class PageHook(View):
    def post(self):
        logger.warning(self.request.post())
        # TODO figure out how to process data to add posts to the website as they are posted to facebook.
