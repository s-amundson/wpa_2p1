from ..models import BeginnerClass
from event.models import Event

import logging
logger = logging.getLogger(__name__)


def create_beginner_class(date, state, class_type, beginner_limit=2, returnee_limit=2):
    return BeginnerClass.objects.create(
        class_date=date,
        class_type=class_type,
        beginner_limit=beginner_limit,
        returnee_limit=returnee_limit,
        event=Event.objects.create(
            event_date=date,
            cost_standard=5,
            cost_member=5,
            state=state,
            type='class'
        )
    )
