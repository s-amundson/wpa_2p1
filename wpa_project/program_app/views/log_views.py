from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView

from event.models import RegistrationAdmin

import logging
logger = logging.getLogger(__name__)


class AdminRegistrationListView(UserPassesTestMixin, ListView):
    model = RegistrationAdmin
    template_name = 'program_app/class_registration_admin_list.html'
    paginate_by = 20

    def get_queryset(self):
        return RegistrationAdmin.objects.all().order_by('-id')

    def test_func(self):
        return self.request.user.is_board
