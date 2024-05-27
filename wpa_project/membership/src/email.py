from django.template.loader import get_template
from django.utils import timezone
from student_app.models import Student, User
from _email.src import EmailMessage
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMessage):
    def election_notification(self, election, opened):
        students = Student.objects.filter(member__expire_date__gte=timezone.now())
        email_users = User.objects.none()
        for student in students:
            email_users = email_users | student.get_user()
        message = f'Woodley Park Archers will be having an election on '
        d = {'election': election, 'opened': opened,
             'pres': election.electioncandidate_set.filter(position=1),
             'vp': election.electioncandidate_set.filter(position=2),
             'sec': election.electioncandidate_set.filter(position=3),
             'tres': election.electioncandidate_set.filter(position=4),
             'mal': election.electioncandidate_set.filter(position=5)}
        logger.warning(d)
        self.send_mass_bcc(email_users, 'WPA Election Notification',
                           get_template('membership/email/election_notification.txt').render(d),
                           get_template('membership/email/election_notification.html').render(d))

    def expire_notice(self, member):
        """ Send a notice to a member to let them know that their membership is going to expire"""

        self.get_email_address(member.student.user)
        logger.warning(self.to)
        d = {'name': f'{member.student.first_name} {member.student.last_name}', 'expire_date': member.expire_date}
        self.subject = 'Woodley Park Archers Membership Expiring'
        self.body = get_template('membership/email/expire_email.txt').render(d)
        self.attach_alternative(get_template('membership/email/expire_email.html').render(d), 'text/html')
        self.send()
