import logging
from captcha.fields import CaptchaField

from src.model_form import MyModelForm
from ..models import Message
logger = logging.getLogger(__name__)


class MessageForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Message
        required_fields = ['contact_name', 'email', 'category', 'message', 'spam_category']
        optional_fields = []
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        logging.debug(self.instance)
        if not self.user.is_authenticated:
            self.fields['captcha'] = CaptchaField(required=True)
            self.fields.pop('spam_category')
        elif not self.user.is_board:
            self.fields.pop('spam_category')

        self.has_instance = self.instance.id is None
        logging.debug(self.has_instance)
        if not self.has_instance:
            logging.debug(self.fields)
            for f in self.fields:
                self.fields[f].required = False
                self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
