import logging
from ..models import BeginnerClass, ClassRegistration
from django.utils import timezone
logger = logging.getLogger(__name__)


class ClassRegistrationHelper:

    def enrolled_count(self, beginner_class):
        beginner = 0
        staff_count = 0
        returnee = 0
        records = ClassRegistration.objects.filter(beginner_class=beginner_class)
        pay_statuses = ['paid', 'admin']
        for record in records:
            if record.pay_status in pay_statuses:
                try:
                    is_staff = record.student.user.is_staff
                except (record.student.DoesNotExist, AttributeError):
                    is_staff = False
                # if record.student.safety_class is not None:
                #     bcd = beginner_class.class_date.date()
                #     scd = record.student.safety_class
                #     logging.debug(f'safety_class={scd}, beginner_class={bcd}, beginner={scd>=bcd}')
                if is_staff:
                    staff_count += 1
                elif record.student.safety_class is None \
                        or record.student.safety_class >= beginner_class.class_date.date():
                    beginner += 1
                else:
                    returnee += 1
        return {'beginner': beginner, 'staff': staff_count, 'returnee': returnee}

    def update_class_state(self, beginner_class):
        records = ClassRegistration.objects.filter(beginner_class=beginner_class)
        records = records.filter(pay_status__in=['paid', 'admin'])
        logging.debug(len(records))
        logging.debug(beginner_class.beginner_limit)
        if beginner_class.class_type == 'beginner' and beginner_class.state in ['open', 'full']:
            if len(records) >= beginner_class.beginner_limit and beginner_class.state == 'open':
                beginner_class.state = 'full'
                beginner_class.save()
            elif len(records) < beginner_class.beginner_limit and beginner_class.state == 'full':
                logging.debug('open')
                beginner_class.state = 'open'
                beginner_class.save()
        elif beginner_class.class_type == 'returnee' and beginner_class.state in ['open', 'full']:
            if len(records) >= beginner_class.returnee_limit and beginner_class.state == 'open':
                beginner_class.state = 'full'
                beginner_class.save()
            elif len(records) < beginner_class.returnee_limit and beginner_class.state == 'full':
                logging.debug('open')
                beginner_class.state = 'open'
                beginner_class.save()
        elif beginner_class.state in ['open', 'full']:
            if len(records.filter(student__safety_class__isnull=True)) >= beginner_class.beginner_limit and \
                    len(records.filter(student__safety_class__isnull=False)) >= beginner_class.returnee_limit and \
                    beginner_class.state == 'open':
                beginner_class.state = 'full'
                beginner_class.save()
            elif len(records.filter(student__safety_class__isnull=True)) < beginner_class.beginner_limit and \
                    len(records.filter(student__safety_class__isnull=False)) < beginner_class.returnee_limit and \
                    beginner_class.state == 'full':
                beginner_class.state = 'open'
                beginner_class.save()
        logging.debug(beginner_class.state)
