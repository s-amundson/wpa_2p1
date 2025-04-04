from django.template.loader import get_template
from django.utils import timezone
from student_app.models import Student, User
from _email.src import EmailMessage
import logging
from ..views import ElectionResultView

logger = logging.getLogger(__name__)


class EmailMessage(EmailMessage):
    email_users = User.objects.none()
    def election_notification(self, election):
        self.get_users()
        d = {'election': election,
             'pres': election.electioncandidate_set.filter(position=1),
             'vp': election.electioncandidate_set.filter(position=2),
             'sec': election.electioncandidate_set.filter(position=3),
             'tres': election.electioncandidate_set.filter(position=4),
             'mal': election.electioncandidate_set.filter(position=5)}
        # logger.warning(d)
        self.send_mass_bcc(self.email_users, 'WPA Election Notification',
                           get_template('membership/email/election_notification.txt').render(d),
                           get_template('membership/email/election_notification.html').render(d))

    def election_result(self, election):
        self.get_users()
        erv = ElectionResultView()
        context = erv.get_result(election)
        self.send_mass_bcc(self.email_users, 'WPA Election Results',
                           get_template('membership/email/election_result.txt').render(context),
                           get_template('membership/email/election_result.html').render(context))

    def expire_notice(self, member):
        """ Send a notice to a member to let them know that their membership is going to expire"""

        self.get_email_address(member.student.user)
        logger.warning(self.to)
        d = {'name': f'{member.student.first_name} {member.student.last_name}', 'expire_date': member.expire_date}
        self.subject = 'Woodley Park Archers Membership Expiring'
        self.body = get_template('membership/email/expire_email.txt').render(d)
        self.attach_alternative(get_template('membership/email/expire_email.html').render(d), 'text/html')
        self.send()

    def get_users(self):
        students = Student.objects.filter(member__expire_date__gte=timezone.now())
        self.email_users = User.objects.none()
        for student in students:
            self.email_users = self.email_users | student.get_user()