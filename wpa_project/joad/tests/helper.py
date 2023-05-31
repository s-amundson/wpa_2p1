from ..models import JoadEvent
from event.models import Event

import logging
logger = logging.getLogger(__name__)


# def create_beginner_class(date, state, class_type, beginner_limit=2, returnee_limit=2):
#     return BeginnerClass.objects.create(
#         class_type=class_type,
#         beginner_limit=beginner_limit,
#         returnee_limit=returnee_limit,
#         event=Event.objects.create(
#             event_date=date,
#             cost_standard=5,
#             cost_member=5,
#             state=state,
#             type='class'
#         )
#     )

def create_joad_event(date, state):
    return JoadEvent.objects.create(
        event=Event.objects.create(
            cost_standard=15,
            cost_member=15,
            event_date=date,
            state=state,
            type='joad class'),
        event_type="joad_indoor",
        student_limit=10,
        pin_cost=5)