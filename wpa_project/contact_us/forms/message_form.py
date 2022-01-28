import logging
from django.forms import ModelForm
from src.model_form import MyModelForm
from ..models import Category, Message
logger = logging.getLogger(__name__)


class MessageForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Message
        required_fields = ['contact_name', 'email', 'category', 'message']
        optional_fields = []
        fields = optional_fields + required_fields

    def send_email(self):
        logging.debug(self.cleaned_data)
