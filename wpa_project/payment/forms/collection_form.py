from django import forms

from ..models import Collections

import logging
logger = logging.getLogger(__name__)


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collections
        fields = ( 'collected_date', 'cash','treasurer', 'board_member', 'note')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['treasurer'].queryset = self.fields['treasurer'].queryset.filter(user__is_board=True)
        self.fields['board_member'].queryset = self.fields['board_member'].queryset.filter(user__is_board=True)
        self.fields['treasurer'].label = 'Treasurer/Delegate'
        self.fields['note'].required = False
        logger.debug(kwargs)

    def clean(self):
        data = super().clean()
        if data['treasurer'] == data['board_member']:
            self.add_error('treasurer', 'Fields must not be the same person.')
            self.add_error('board_member', 'Fields must not be the same person.')