from django.template.loader import get_template
from _email.src import EmailMessage as EM

import logging

logger = logging.getLogger(__name__)


class EmailMessage(EM):
    def awrl_email(self, student):
        if not student.signature_pdf:
            logging.warning("No signature to send")
            return
        if student.user is not None:
            self.get_email_address(student.user)
            name = f'{student.first_name} {student.last_name}'
        else:
            students = student.student_family.student_set.all().order_by('id')
            for s in students:
                # logging.debug(f'id: {s.id}, user: {s.user}')
                if s.user is not None:
                    self.get_email_address(s.user)
                    name = f'{s.first_name} {s.last_name}'
                    break
        self.subject = "Woodley Park Archers AWRL agreement"
        student_name = f'{student.first_name} {student.last_name}'
        d = {'name': name,
             'message': f'Attached is the Accident Waiver and Release of Liability for {student_name}'}
        self.body = get_template('student_app/email/simple_message.txt').render(d)
        self.attach_alternative(get_template('student_app/email/simple_message.html').render(d), 'text/html')
        self.attach(f'{student_name}.pdf', student.signature_pdf.read())
        self.send()
