from django.forms import HiddenInput, BooleanField, CheckboxInput, DateTimeInput, SplitDateTimeField
from django.utils import timezone
import logging
from src.model_form import MyModelForm
from ..models import Election, ElectionCandidate, ElectionVote
logger = logging.getLogger(__name__)


class ElectionForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Election
        fields = ['election_date', 'state', 'description', 'election_close']
        hidden_fields = []
        optional_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['election_date'].widget = DateTimeInput()
        self.fields['election_date'].initial = timezone.now() + timezone.timedelta(days=30)

        self.fields['election_close'].widget = DateTimeInput()
        self.fields['election_close'].required = False
        self.fields['notify'] = BooleanField(widget=CheckboxInput(
                attrs={'class': "m-2"}), required=False, label="Send out notification email to members")
        if self.instance.id:
            logger.warning(self.instance.electioncandidate_set.all())
        self.close_updated = False

    def clean(self):
        cleaned_data = super().clean()
        logger.warning(cleaned_data)
        if cleaned_data['election_close'] is None:
            cleaned_data['election_close'] = cleaned_data['election_date'] + timezone.timedelta(days=1)
            self.close_updated = True
        return cleaned_data

class ElectionCanidateForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = ElectionCandidate
        required_fields = ['position', 'student']
        hidden_fields = ['election', ]
        optional_fields = []
        fields = required_fields + hidden_fields

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        if type(self.initial['election']) == int:
            election = Election.objects.get(pk=self.initial['election'])
        else:
            election = self.initial['election']
        d = election.election_date
        d = d.replace(year=d.year-18)
        self.fields['student'].queryset = self.fields['student'].queryset.filter(
            dob__lte=d, member__expire_date__gte=election.election_date)
        self.fields['election'].label = ""


class ElectionVoteForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = ElectionVote
        required_fields = ['election', 'member']
        hidden_fields = []
        optional_fields = ['president', 'vice_president', 'secretary', 'treasurer', 'member_at_large']
        fields = required_fields + hidden_fields + optional_fields

    def __init__(self,  *args, **kwargs):
        members = kwargs.pop('members')
        super().__init__(*args, **kwargs)
        self.election_date = self.initial['election'].election_date
        self.fields['member'].queryset = members
        self.fields['member'].initial = members.last()
        # self.fields['member'].disabled = True
        # self.fields['member'].hidden = True
        self.fields['election'].widget = HiddenInput()
        self.fields['member'].widget = HiddenInput()

        # limit the canidates to this election
        for f in self.Meta.optional_fields:
            self.fields[f].queryset = self.fields[f].queryset.filter(election=self.initial['election'])
