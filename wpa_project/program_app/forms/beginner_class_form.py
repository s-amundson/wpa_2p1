from django.forms import ModelForm

from ..models import BeginnerClass

import logging
logger = logging.getLogger(__name__)


class BeginnerClassForm(ModelForm):

    class Meta:
        model = BeginnerClass
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # logging.debug(self.instance)
        # logging.debug(self.instance is not None)
