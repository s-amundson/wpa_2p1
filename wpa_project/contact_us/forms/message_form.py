import logging
from src.model_form import MyModelForm
from ..models import Message
from ..src import EmailMessage
logger = logging.getLogger(__name__)


class MessageForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Message
        required_fields = ['contact_name', 'email', 'category', 'message']
        optional_fields = []
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.debug(self.instance)

        self.has_instance = self.instance.id is None
        logging.debug(self.has_instance)
        if not self.has_instance:
            logging.debug(self.fields)
            for f in self.fields:
                self.fields[f].required = False
                self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'disabled': 'disabled'})

    def send_email(self, message):
        EmailMessage().contact_email(message)
