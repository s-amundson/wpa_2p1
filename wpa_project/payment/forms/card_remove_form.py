from django import forms

from ..models import Card, Customer, PaymentLog

import logging
logger = logging.getLogger(__name__)


class CardRemoveForm(forms.Form):
    card = forms.ChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        logging.debug(user)
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['card'].choices = self.card_choices()

    def card_choices(self):
        saved_cards = Card.objects.filter(customer__user=self.user, enabled=True)
        card_choices = []
        for card in saved_cards:
            card_choices.append((card.id, str(card)))
        card_choices.append((0, "New Card"))
        logging.debug(card_choices)
        return card_choices
