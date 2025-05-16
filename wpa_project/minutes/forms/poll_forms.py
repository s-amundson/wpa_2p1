import logging
from src.model_form import MyModelForm
from django.forms import BooleanField, ModelForm, CheckboxInput, HiddenInput

from ..models import Poll, PollVote

logger = logging.getLogger(__name__)


class PollForm(MyModelForm):
    template_name = 'minutes/forms/poll_form.html'

    class Meta(MyModelForm.Meta):
        model = Poll
        exclude = []
        hidden_fields = ['minutes', 'business', 'poll_type']
        optional_fields = ['is_anonymous']
        required_fields = ['description', 'poll_choices', 'level', 'state', 'duration']
        fields =required_fields + optional_fields + hidden_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_anonymous'] = BooleanField(
            widget=CheckboxInput(attrs={'class': "m-2"}),
            required=False,
            initial=False,
            label='Anonymous Voting')
        self.fields['state'].initial = 'open'
        self.fields['level'].initial = 'board'

        self.fields['duration'].label += " (hours)"
        self.fields['minutes'].widget = HiddenInput()
        self.fields['business'].widget = HiddenInput()
        self.fields['poll_type'].widget = HiddenInput()

        logger.warning(self.is_bound)
        logger.warning(self.instance.poll_type)
        if self.instance.id:
            pass
        elif (not self.is_bound and kwargs['initial'].get('poll_type', None) is not None
                and kwargs['initial']['poll_type'].poll_type == 'motion'):

            self.fields['poll_choices'].queryset = self.fields['poll_choices'].queryset[:3]
            self.fields['poll_choices'].initial = self.fields['poll_choices'].queryset


class PollVoteForm(ModelForm):
    template_name = 'minutes/forms/poll_vote_form.html'
    class Meta():
        model = PollVote
        fields = ['poll', 'user', 'choice']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['poll'].widget = HiddenInput()
        self.fields['user'].widget = HiddenInput()
