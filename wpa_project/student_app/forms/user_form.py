from src import MyModelForm
from django.forms.widgets import CheckboxInput, SelectDateWidget
from django.utils.datetime_safe import date

from ..models import User
import logging
logger = logging.getLogger(__name__)


class UserForm(MyModelForm):

    class Meta(MyModelForm.Meta):

        model = User
        disabled_fields = ['is_member']
        hidden_fields = []
        optional_fields = ['is_board', 'is_staff', 'is_instructor', 'instructor_expire_date', 'dark_theme', 'is_active']
        required_fields = []
        fields = optional_fields + hidden_fields + disabled_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['is_board', 'is_staff', 'is_instructor', 'dark_theme', 'is_active', 'is_member']:
            self.fields[f].widget = CheckboxInput()
            self.fields[f].required = False

        self.fields['is_member'].widget.attrs.update({'disabled': 'disabled'})
        self.fields['instructor_expire_date'].widget = SelectDateWidget(
            years=range(date.today().year, date.today().year + 3, 1))
        # self.fields['instructor_expire_date'].widget.attrs.update({'class': 'form-control'})
