import logging
from django.conf import settings
from django.utils import timezone
from django.forms import BooleanField, CheckboxInput, SelectDateWidget
from src.model_form import MyModelForm
from ..models import Complaint, ComplaintComment
logger = logging.getLogger(__name__)


class ComplaintForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Complaint
        required_fields = ['category', 'incident_date', 'message']
        optional_fields = []
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['incident_date'].required = False
        self.fields['incident_date'].label = 'Incident Date (optional)'
        self.fields['incident_date'].widget = SelectDateWidget(
            years=range(timezone.datetime.today().year, timezone.datetime.today().year - 2, -1))
        self.fields['incident_date'].widget.attrs.update({'class': 'm-2'})
        self.fields['anonymous'] = BooleanField(
            widget=CheckboxInput(attrs={'class': "m-2"}),
            required=False,
            initial=True,
            label='I wish to make an anonymous complaint')
        self.fields['resolved'] = BooleanField(
            widget=CheckboxInput(attrs={'class': "m-2"}),
            required=False,
            initial=False,
            label='This complaint has been resolved')
        if self.instance.id:
            for f in ['category', 'incident_date', 'message', 'anonymous']:
                self.fields[f].widget.attrs.update({'readonly': 'readonly'})

class ComplientCommentForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = ComplaintComment
        required_fields = ['comment']
        hidden_fields = ['complaint']
        read_fields = ['comment_date']
        fields = hidden_fields + required_fields + read_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['complaint'].label = ""
        self.fields['comment_date'].initial = ''
