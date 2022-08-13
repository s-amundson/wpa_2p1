import logging
from django.db.models import Count

from .email import EmailMessage
from ..models import BeginnerClass, ClassRegistration
from student_app.models import Student
from payment.src import PaymentHelper

from django.utils import timezone
logger = logging.getLogger(__name__)


class ClassRegistrationHelper:
    def attendance_history_queryset(self, student_family):
        if student_family is None:
            return ClassRegistration.objects.none()
        object_list = []
        students = student_family.student_set.all()
        # logging.debug(students)
        cr = ClassRegistration.objects.filter(
            beginner_class__class_date__lt=timezone.now().today(),
            student__in=students,
            pay_status__in=['paid', 'admin'])
        for student in students:
            sr = cr.filter(student=student).aggregate(attended_count=Count('attended', distinct=True),
                                                      registrations=Count('id', distinct=True))
            # logging.debug(sr)
            sr['student'] = student
            object_list.append(sr)
        return object_list

    def charge_group(self, queryset):
        for ikey in queryset.values('idempotency_key').annotate(ik_count=Count('idempotency_key')).order_by():
            logging.debug(ikey)
            icr = queryset.filter(idempotency_key=str(ikey['idempotency_key']))
            cost = icr[0].beginner_class.cost
            note = f'Class on {str(icr[0].beginner_class.class_date)[:10]}, Students: '
            for cr in icr:
                note += f'{cr.student.first_name}, '
            payment = None
            if cr.user.customer_set.last():
                card = cr.user.customer_set.last().card_set.filter(enabled=True, default=True).last()
                payment = PaymentHelper(cr.user).create_payment(cost * 100 * ikey['ik_count'], 'intro', 0,
                                                                str(ikey['idempotency_key']), note, '',
                                                                saved_card_id=card.id)
                # send email to user
            if payment is None:  # a payment error happened
                icr.update(pay_status='start')

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

    def has_space(self, user, beginner_class, beginner, instructor, returnee):
        enrolled_count = self.enrolled_count(beginner_class)
        logging.debug(enrolled_count)
        logging.debug(beginner)
        wait = False
        if beginner_class.state in ['open', 'wait']:  # in case it changed since user got the self.form.
            if beginner and enrolled_count['beginner'] + beginner > beginner_class.beginner_limit:
                if beginner and enrolled_count['beginner'] + beginner > beginner_class.beginner_limit + \
                        beginner_class.beginner_wait_limit:
                    return 'full'
                if enrolled_count['beginner'] + beginner > beginner_class.beginner_limit:
                    wait = True

            if returnee and enrolled_count['returnee'] + returnee > beginner_class.returnee_limit:
                if returnee and enrolled_count['returnee'] + returnee > beginner_class.returnee_limit + \
                        beginner_class.returneewait_limit:
                    return 'full'
                if enrolled_count['returnee'] + returnee > beginner_class.returnee_limit:
                    wait = True

            if instructor and enrolled_count['staff'] + instructor > beginner_class.instructor_limit:
                return 'full'
            if wait:
                return 'wait'
            return 'open'

        elif beginner_class.state in ['full', 'closed'] and user.is_staff:
            if instructor and enrolled_count['staff'] + instructor > beginner_class.instructor_limit:
                return 'full'
            else:
                return 'open'

    def student_registrations(self, beginner_class):
        return ClassRegistration.objects.filter(
            beginner_class=beginner_class,pay_status__in=['paid', 'admin', 'waiting']).exclude(
            student__user__is_staff=True)

    def update_class_state(self, beginner_class):
        records = self.student_registrations(beginner_class)
        logging.debug(len(records))
        logging.debug(beginner_class.beginner_limit)
        if beginner_class.class_type == 'beginner' and beginner_class.state in ['open', 'wait', 'full']:
            if len(records) >= beginner_class.beginner_limit and beginner_class.state == 'open':
                if len(records) >= beginner_class.beginner_limit + beginner_class.beginner_wait_limit:
                    beginner_class.state = 'full'
                else:
                    beginner_class.state = 'wait'
                beginner_class.save()
            elif len(records) < beginner_class.beginner_limit + beginner_class.beginner_wait_limit and \
                    beginner_class.state in ['wait', 'full']:
                if len(records) < beginner_class.beginner_limit:
                    beginner_class.state = 'open'
                else:
                    beginner_class.state = 'wait'
                beginner_class.save()
        elif beginner_class.class_type == 'returnee' and beginner_class.state in ['open', 'wait', 'full']:
            if len(records) >= beginner_class.returnee_limit and beginner_class.state == 'open':
                if len(records) >= beginner_class.returnee_limit + beginner_class.returnee_wait_limit:
                    beginner_class.state = 'full'
                else:
                    beginner_class.state = 'wait'
                beginner_class.save()
            elif len(records) < beginner_class.returnee_limit + beginner_class.returnee_wait_limit and \
                    beginner_class.state in ['wait', 'full']:
                if len(records) < beginner_class.returnee_limit:
                    beginner_class.state = 'open'
                else:
                    beginner_class.state = 'wait'
                beginner_class.save()
        elif beginner_class.state in ['open', 'wait', 'full']:
            beginners = len(records.filter(student__safety_class__isnull=True))
            returnees = len(records.filter(student__safety_class__isnull=False))
            if beginners >= beginner_class.beginner_limit and returnees >= beginner_class.returnee_limit and \
                    beginner_class.state == 'open':
                if beginners >= beginner_class.beginner_limit + beginner_class.beginner_wait_limit and \
                        returnees >= beginner_class.returnee_limit + beginner_class.returnee_wait_limit:
                    beginner_class.state = 'full'
                else:
                    beginner_class.state = 'wait'
                beginner_class.save()
            elif beginners < beginner_class.beginner_limit + beginner_class.beginner_wait_limit and \
                    returnees < beginner_class.returnee_limit + beginner_class.returnee_wait_limit and \
                    beginner_class.state in ['wait', 'full']:
                if beginners < beginner_class.beginner_limit and returnees < beginner_class.returnee_limit:
                    beginner_class.state = 'open'
                else:
                    beginner_class.state = 'wait'
                beginner_class.save()
        # logging.debug(beginner_class.state)

    def update_waiting(self, beginner_class):
        records = self.student_registrations(beginner_class)
        logging.debug(records)
        waiting = records.filter(pay_status='waiting').order_by('modified')
        admitted = records.filter(pay_status__in=['paid', 'admin']).order_by('modified')

        if not len(waiting):
            return
        if beginner_class.class_type == 'beginner':
            if len(admitted) < beginner_class.beginner_limit:
                logging.debug(f'space available {beginner_class.beginner_limit - len(admitted)}')
                next_group = waiting.filter(idempotency_key=waiting.first().idempotency_key)
                logging.debug(f'next group {len(next_group)}')
                if beginner_class.beginner_limit - len(admitted) >= len(next_group):
                    self.charge_group(next_group)
                    EmailMessage().wait_list_off(next_group)
                    # self.update_waiting(beginner_class)
        elif beginner_class.class_type == 'returnee':
            if len(admitted) < beginner_class.returnee_limit:
                logging.debug(f'space available {beginner_class.returnee_limit - len(admitted)}')
                next_group = waiting.filter(idempotency_key=waiting.first().idempotency_key)
                logging.debug(f'next group {len(next_group)}')
                if beginner_class.returnee_limit - len(admitted) >= len(next_group):
                    self.charge_group(next_group)
                    EmailMessage().wait_list_off(next_group)

