import logging
from ..models import BeginnerClass, ClassRegistration
from django.utils import timezone
logger = logging.getLogger(__name__)


class ClassRegistrationHelper:
    def check_space(self, class_registration_dict, update=False):
        # {'beginner_class': beginner_class.id, 'beginner': beginner,
        #  'returnee': returnee}
        is_space = True
        bc = BeginnerClass.objects.get(pk=class_registration_dict['beginner_class'])
        ec = self.enrolled_count(bc)
        logging.debug(class_registration_dict)
        if class_registration_dict['beginner'] and ec['beginner'] + class_registration_dict['beginner'] > bc.beginner_limit:
            is_space = False
        if class_registration_dict['returnee'] and ec['returnee'] + class_registration_dict['returnee'] > bc.returnee_limit:
            is_space = False
        if ec['beginner'] + class_registration_dict['beginner'] == bc.beginner_limit and \
           ec['returnee'] + class_registration_dict['returnee'] == bc.returnee_limit:
            if update:
                bc.state = 'full'
                bc.save()
        logging.debug(is_space)
        return is_space

    def enrolled_count(self, beginner_class):
        # bc = self.objects.get(beginner_class)
        beginner = 0
        instructors = 0
        returnee = 0
        records = ClassRegistration.objects.filter(beginner_class=beginner_class)
        pay_statuses = ['paid']
        for record in records:
            # logging.debug(f'safety_class {record.student.safety_class}, pay_status {record.pay_status}')
            if record.pay_status in pay_statuses:
                try:
                    instructor = record.student.user.is_instructor
                except (record.student.DoesNotExist, AttributeError):
                    instructor = False
                if instructor:
                    instructors += 1
                elif record.student.safety_class:
                    returnee += 1
                else:
                    beginner += 1
        return {'beginner': beginner, 'instructors': instructors, 'returnee': returnee}
