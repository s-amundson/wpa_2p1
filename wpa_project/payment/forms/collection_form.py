from django import forms
from django.db.models import Q

from ..models import Collections

import logging
logger = logging.getLogger(__name__)


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collections
        fields = ( 'collected_date', 'cash','treasurer', 'board_member', 'note')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['treasurer'].label = 'Treasurer/Delegate'
        self.fields['note'].required = False
        if self.instance.id:
            logger.warning(self.instance.correction)
            if self.instance.correction:
                for f in self.Meta.fields:
                    self.fields[f].widget.attrs.update({'disabled': 'disabled'})
            self.fields['treasurer'].queryset = self.fields['treasurer'].queryset.filter(
                Q(user__is_board=True) | Q(pk=self.instance.treasurer.id))
            self.fields['board_member'].queryset = self.fields['board_member'].queryset.filter(
                Q(user__is_board=True) | Q(pk=self.instance.board_member.id))
        else:
            self.fields['treasurer'].queryset = self.fields['treasurer'].queryset.filter(user__is_board=True)
            self.fields['board_member'].queryset = self.fields['board_member'].queryset.filter(user__is_board=True)

    def clean(self):
        data = super().clean()
        if data['treasurer'] == data['board_member']:
            self.add_error('treasurer', 'Fields must not be the same person.')
            self.add_error('board_member', 'Fields must not be the same person.')