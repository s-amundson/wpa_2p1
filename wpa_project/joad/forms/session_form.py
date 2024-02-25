from django.forms import SelectDateWidget
from django.utils import timezone
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
            years=range(timezone.datetime.today().year, timezone.datetime.today().year + 3, 1))
