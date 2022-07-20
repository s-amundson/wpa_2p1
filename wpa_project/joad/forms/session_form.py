from django.forms import SelectDateWidget
from django.utils.datetime_safe import date
import logging
from src.model_form import MyModelForm
from ..models import Session
logger = logging.getLogger(__name__)


class SessionForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Session
        fields = ['cost', 'start_date', 'state', 'student_limit']
        hidden_fields = []
        optional_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget = SelectDateWidget(
            years=range(date.today().year, date.today().year + 3, 1))
