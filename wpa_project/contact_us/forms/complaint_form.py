import logging
from django.conf import settings
from django.utils import timezone
from django.forms import BooleanField, CheckboxInput, SelectDateWidget
from src.model_form import MyModelForm
from ..models import Complaint, ComplaintComment
from student_app.models import User
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
                self.fields[f].disabled = True
            if self.instance.resolved_date is not None:
                self.fields['resolved'].initial = True


class ComplaintCommentForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = ComplaintComment
        required_fields = ['comment']
        hidden_fields = ['complaint', 'user']
        read_fields = ['comment_date',]
        fields = required_fields + hidden_fields + read_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.warning(self.initial)
        self.fields['complaint'].label = ""
        self.fields['comment_date'].initial = ''
        if self.instance.user:
            self.fields['comment'].disabled = True
            self.student = self.instance.user.student_set.last()
        else:
            self.student = self.initial.get('student', None)
        self.fields['comment'].widget.attrs.update({'cols': 80, 'rows': 3})

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.id is None:
            if len(cleaned_data['comment']):
                cleaned_data['comment_date'] = timezone.now()
        return cleaned_data
