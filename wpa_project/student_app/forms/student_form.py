from src import MyModelForm
from django.forms import SelectDateWidget
from django.utils.datetime_safe import date

from ..models import Student
import logging
logger = logging.getLogger(__name__)


class StudentForm(MyModelForm):

    class Meta(MyModelForm.Meta):

        model = Student
        disabled_fields = []
        hidden_fields = []
        optional_fields = ['email', 'safety_class']
        required_fields = ['first_name', 'last_name', 'dob']
        fields = optional_fields + hidden_fields + disabled_fields + required_fields

    def __init__(self, *args, **kwargs):
        student_is_user = kwargs.get('student_is_user', False)
        if 'student_is_user' in kwargs:
            kwargs.pop('student_is_user')
        super().__init__(*args, **kwargs)
        self.fields['dob'].widget = SelectDateWidget(years=range(date.today().year, date.today().year - 100, -1))
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
        self.fields['dob'].label = "Date of Birth"
        self.fields['safety_class'].widget = SelectDateWidget(years=range(date.today().year, 2019, -1))

        if student_is_user:
            self.fields['email'].widget.attrs.update({'disabled': 'disabled'})
        else:
            self.fields['email'].widget.attrs.update({'placeholder': 'Email (optional)'})
