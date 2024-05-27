
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from ..models import Election, ElectionCandidate, ElectionPosition, ElectionVote, Level, Member
from ..src.email import EmailMessage
from ..tasks import membership_election_calendar_notify
from student_app.models import Student, User
from _email.models import BulkEmail

import logging
logger = logging.getLogger(__name__)


class TestsElection(TestCase):
    # fixtures = ['member1', 'level']
    fixtures = ['f1', 'level', 'member1']

    candidates = []

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def make_election(self):
        d = timezone.now() + timezone.timedelta(days=3)
        d = d.replace(hour=19, minute=30)
        election = Election.objects.create(
            election_date=d,
            state='open',
            election_close=d + timezone.timedelta(days=1),
            description="Join Zoom Meeting ID: 123 1234 1234\n\nhttps://us02web.zoom.us/j/1231231234"
        )
        pos =      [1,  1,  2,  2,  3,  3,  4,  4,  4,  5,  5,  5,  5,  5]
        students = [9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24]
        #  Two running for President, two for vice, 2 for Secretary, 3 for treasure and 5 at large
        for i in range(len(pos)):
            self.candidates.append(ElectionCandidate.objects.create(
                election=election,
                position=ElectionPosition.objects.get(pk=pos[i]),
                student=Student.objects.get(pk=students[i])
            ))
        return election

    def vote(self, election, member, pres, vice, sec, treas, large ):
        large_canidates = []
        for i in large:
            large_canidates.append(self.candidates[i])

        ev = ElectionVote.objects.create(
            election=election,
            president=self.candidates[pres],
            vice_president=self.candidates[vice],
            secretary=self.candidates[sec],
            treasurer=self.candidates[treas],
            member=Member.objects.get(pk=member)
        )
        ev.member_at_large.set(large_canidates)
        return ev

    def test_election_form_get_page(self):
        # Get the page, if not super or board, page is forbidden
        response = self.client.get(reverse('membership:election'), secure=True)
        self.assertTemplateUsed(response, 'membership/election_form.html')
        self.assertEqual(response.status_code, 200)

    # @tag('temp')
    def test_election_form_post_good(self):
        d = timezone.now() + timezone.timedelta(days=3)
        d_close = d + timezone.timedelta(days=1)
        response = self.client.post(reverse('membership:election'),
                                    {'election_date': d, 'state': 'open',
                                     'election_close': d_close},
                                   secure=True)
        # self.assertEqual(response.status_code, 200)
        elections = Election.objects.all()
        self.assertEqual(len(elections), 1)
        self.assertEqual(elections[0].election_date, d)
        pt = PeriodicTask.objects.filter(name='Election Close')
        self.assertEqual(pt.count(), 1)
        ct = CrontabSchedule.objects.last()
        self.assertEqual(ct.minute, str(d_close.minute))
    #     self.assertRedirects(response, reverse('membership:election', kwargs={'election_id': elections[0].id}))

    def test_election_form_post_error(self):
        d = timezone.now().date() + timezone.timedelta(days=3)
        response = self.client.post(reverse('membership:election'), {'election_date': d},
                                   secure=True)
        self.assertEqual(response.status_code, 200)
        elections = Election.objects.all()
        self.assertEqual(len(elections), 0)

    def test_get_election_list(self):
        # Get the page, if not super or board, page is forbidden
        response = self.client.get(reverse('membership:election_list'), secure=True)
        self.assertTemplateUsed(response, 'membership/election_list.html')
        self.assertEqual(response.status_code, 200)

    def test_get_election_candidate_form(self):
        d = timezone.now().date() + timezone.timedelta(days=3)
        election = Election.objects.create(
            election_date=d,
            state='open'
        )
        response = self.client.get(reverse('membership:election_candidate', kwargs={'election_id': election.id}), secure=True)
        self.assertTemplateUsed(response, 'student_app/form_as_p.html')
        self.assertEqual(response.status_code, 200)

    def test_post_election_candidate_form_good(self):
        d = timezone.now().date() + timezone.timedelta(days=3)
        election = Election.objects.create(
            election_date=d,
            state='open'
        )
        response = self.client.post(reverse('membership:election_candidate', kwargs={'election_id': election.id}),
                                    {'election': election.id, 'position': 1, 'student': 9}, secure=True)
        ec = ElectionCandidate.objects.all()
        self.assertEqual(len(ec), 1)
        self.assertEqual(str(ec[0].position), 'President')

    def test_post_election_candidate_form_error(self):
        d = timezone.now().date() + timezone.timedelta(days=3)
        election = Election.objects.create(
            election_date=d,
            state='open'
        )
        student = Student.objects.get(pk=7)
        student.dob = d.replace(year=d.year - 10) # 10 year-olds cannot be on board.
        student.save()

        response = self.client.post(reverse('membership:election_candidate', kwargs={'election_id': election.id}),
                                    {'election': election.id, 'position': 1, 'student': 7}, secure=True)
        ec = ElectionCandidate.objects.all()
        self.assertEqual(len(ec), 0)
        self.assertContains(response, 'Select a valid choice. That choice is not one of the available choices.')

    def test_election_vote_get(self):
        d = timezone.now().date() + timezone.timedelta(days=3)
        election = Election.objects.create(
            election_date=d,
            state='open'
        )
        member = Member.objects.create(
            student=self.test_user.student_set.last(),
            expire_date=d,
            level=Level.objects.get(pk=1),
            join_date=d.replace(year=d.year - 1),
            begin_date=d.replace(year=d.year - 3)
        )
        response = self.client.get(reverse('membership:election_vote', kwargs={'election_id': election.id}), secure=True)
        self.assertTemplateUsed(response, 'membership/election_vote_form.html')
        self.assertEqual(response.status_code, 200)

    # @tag('temp')
    def test_election_vote_get_noauth(self):

        d = timezone.now().date() + timezone.timedelta(days=3)
        election = Election.objects.create(
            election_date=d,
            state='open'
        )
        member = Member.objects.create(
            student=self.test_user.student_set.last(),
            expire_date=d,
            level=Level.objects.get(pk=1),
            join_date=d.replace(year=d.year - 1),
            begin_date=d.replace(year=d.year - 3)
        )
        self.client.logout()
        response = self.client.get(reverse('membership:election_vote', kwargs={'election_id': election.id}), secure=True)
        self.assertRedirects(response, reverse('account_login') + '?next='
                             + reverse('membership:election_vote', kwargs={'election_id': election.id}))

    def test_election_vote_get_scheduled(self):
        d = timezone.now().date() + timezone.timedelta(days=3)
        election = Election.objects.create(
            election_date=d,
            state='scheduled'
        )
        member = Member.objects.create(
            student=self.test_user.student_set.last(),
            expire_date=d,
            level=Level.objects.get(pk=1),
            join_date=d.replace(year=d.year - 1),
            begin_date=d.replace(year=d.year - 3)
        )
        response = self.client.get(reverse('membership:election_vote', kwargs={'election_id': election.id}), secure=True)
        self.assertRedirects(response, reverse('membership:election_list'))

    def test_vote_good(self):
        election = self.make_election()
        d = timezone.now().date() + timezone.timedelta(days=3)
        member = Member.objects.create(
            student=self.test_user.student_set.last(),
            expire_date=d,
            level=Level.objects.get(pk=1),
            join_date=d.replace(year=d.year - 1),
            begin_date=d.replace(year=d.year - 3)
        )

        response = self.client.post(reverse('membership:election_vote', kwargs={'election_id': election.id}),
                                        {'election': election.id,
                                         'member': member.id,
                                         'president': 2,
                                         'vice_president': 4,
                                         'secretary': 5,
                                         'treasurer': 7,
                                         'member_at_large': [11,12,14]},
                                    secure=True)
        self.assertRedirects(response, reverse('membership:election_vote', kwargs={'election_id': election.id}))
        ev = ElectionVote.objects.all()
        self.assertEqual(len(ev), 1)
        ev = ev[0]
        #         pos =      [1,  1,  2,  2,  3,  3,  4,  4,  4,  5,  5,  5,  5,  5]
        #         students = [9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24]
        #                     1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14

        self.assertEqual(ev.president.student, Student.objects.get(pk=10))
        self.assertEqual(ev.vice_president.student, Student.objects.get(pk=12))
        self.assertEqual(ev.secretary.student, Student.objects.get(pk=14))
        self.assertEqual(ev.treasurer.student, Student.objects.get(pk=16))
        self.assertIn(Student.objects.get(pk=22).electioncandidate_set.last(), ev.member_at_large.all())

    def test_vote_good_not_all(self):
        election = self.make_election()
        d = timezone.now().date() + timezone.timedelta(days=3)
        member = Member.objects.create(
            student=self.test_user.student_set.last(),
            expire_date=d,
            level=Level.objects.get(pk=1),
            join_date=d.replace(year=d.year - 1),
            begin_date=d.replace(year=d.year - 3)
        )

        response = self.client.post(reverse('membership:election_vote', kwargs={'election_id': election.id}),
                                        {'election': election.id,
                                         'member': member.id,
                                         'president': 2,
                                         'secretary': 5,
                                         'treasurer': 7,
                                         'member_at_large': [12]},
                                    secure=True)
        self.assertRedirects(response, reverse('membership:election_vote', kwargs={'election_id': election.id}))
        ev = ElectionVote.objects.all()
        self.assertEqual(len(ev), 1)
        ev = ev[0]
        #         pos =      [1,  1,  2,  2,  3,  3,  4,  4,  4,  5,  5,  5,  5,  5]
        #         students = [9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24]
        #                     1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14

        self.assertEqual(ev.president.student, Student.objects.get(pk=10))
        self.assertIsNone(ev.vice_president)
        self.assertEqual(ev.secretary.student, Student.objects.get(pk=14))
        self.assertEqual(ev.treasurer.student, Student.objects.get(pk=16))
        self.assertIn(Student.objects.get(pk=22).electioncandidate_set.last(), ev.member_at_large.all())

    def test_vote_error(self):
        election = self.make_election()
        d = timezone.now().date() + timezone.timedelta(days=3)
        member = Member.objects.create(
            student=self.test_user.student_set.last(),
            expire_date=d,
            level=Level.objects.get(pk=1),
            join_date=d.replace(year=d.year - 1),
            begin_date=d.replace(year=d.year - 3)
        )

        response = self.client.post(reverse('membership:election_vote', kwargs={'election_id': election.id}),
                                        {'election': election.id,
                                         'member': member.id,
                                         'president': 2,
                                         'vice_president': 4,
                                         'secretary': 5,
                                         'member_at_large': [11, 12, 13, 14]},
                                    secure=True)
        ev = ElectionVote.objects.all()
        self.assertEqual(len(ev), 0)
        self.assertContains(response, 'To many members selected.')

    def test_vote_good_update_vote(self):
        election = self.make_election()
        d = timezone.now().date() + timezone.timedelta(days=3)
        member = Member.objects.create(
            student=self.test_user.student_set.last(),
            expire_date=d,
            level=Level.objects.get(pk=1),
            join_date=d.replace(year=d.year - 1),
            begin_date=d.replace(year=d.year - 3)
        )

        response = self.client.post(reverse('membership:election_vote', kwargs={'election_id': election.id}),
                                        {'election': election.id,
                                         'member': member.id,
                                         'president': 2,
                                         'secretary': 5,
                                         'treasurer': 7,
                                         'member_at_large': [12]},
                                    secure=True)
        self.assertRedirects(response, reverse('membership:election_vote', kwargs={'election_id': election.id}))
        ev = ElectionVote.objects.all()
        self.assertEqual(len(ev), 1)
        ev = ev[0]

        self.assertEqual(ev.president.student, Student.objects.get(pk=10))
        self.assertIsNone(ev.vice_president)
        self.assertEqual(ev.secretary.student, Student.objects.get(pk=14))
        self.assertEqual(ev.treasurer.student, Student.objects.get(pk=16))
        self.assertIn(Student.objects.get(pk=22).electioncandidate_set.last(), ev.member_at_large.all())

        response = self.client.post(reverse('membership:election_vote', kwargs={'election_id': election.id}),
                                        {'election': election.id,
                                         'member': member.id,
                                         'president': 2,
                                         'vice_president': 4,
                                         'secretary': 5,
                                         'treasurer': 7,
                                         'member_at_large': [12]},
                                    secure=True)
        self.assertRedirects(response, reverse('membership:election_vote', kwargs={'election_id': election.id}))
        ev = ElectionVote.objects.all()
        self.assertEqual(len(ev), 1)
        ev = ev[0]
        self.assertEqual(ev.vice_president.student, Student.objects.get(pk=12))

    def test_vote_election_closed(self):
        election = self.make_election()
        election.state = 'closed'
        election.save()

        d = timezone.now().date() + timezone.timedelta(days=3)
        member = Member.objects.create(
            student=self.test_user.student_set.last(),
            expire_date=d,
            level=Level.objects.get(pk=1),
            join_date=d.replace(year=d.year - 1),
            begin_date=d.replace(year=d.year - 3)
        )

        response = self.client.post(reverse('membership:election_vote', kwargs={'election_id': election.id}),
                                        {'election': election.id,
                                         'member': member.id,
                                         'president': 2,
                                         'vice_president': 4,
                                         'secretary': 5,
                                         'treasurer': 7,
                                         'member_at_large': [11,12,14]},
                                    secure=True)
        ev = ElectionVote.objects.all()
        self.assertEqual(len(ev), 0)
        self.assertRedirects(response, reverse('membership:election_result', kwargs={'election_id': election.id}))

    def test_election_result(self):
        election = self.make_election()
        election.state = 'closed'
        election.save()
        d = timezone.now().date() + timezone.timedelta(days=3)
        member = Member.objects.create(
            student=self.test_user.student_set.last(),
            expire_date=d,
            level=Level.objects.get(pk=1),
            join_date=d.replace(year=d.year - 1),
            begin_date=d.replace(year=d.year - 3)
        )
        #         pos =      [1,  1,  2,  2,  3,  3,  4,  4,  4,    5,  5,  5,  5,  5]
        #         students = [9, 10, 11, 12, 14, 15, 16, 17, 18,   19, 20, 22, 23, 24]
        #                     0,  1,  2,  3,  4,  5,  6,  7,  8,    9, 10, 11, 12, 13
        self.vote(election, 4, 0, 2, 5, 8, [9, 11, 13])
        self.vote(election, 5, 1, 2, 5, 8, [9, 11, 13])
        self.vote(election, 6, 1, 3, 5, 6, [11, 12, 13])
        self.vote(election, 7, 0, 3, 5, 7, [10, 13])
        self.vote(election, 8, 1, 3, 4, 8, [10, 11, 13])
        self.vote(election, 9, 1, 3, 5, 7, [9, 12, 13])

        response = self.client.get(reverse('membership:election_result', kwargs={'election_id': election.id}),
                                   secure=True)

        self.assertEqual(response.context['president'][0]['candidate'], self.candidates[1])
        self.assertEqual(response.context['president'][0]['votes'], 4)
        self.assertFalse(response.context['president'][0]['tie'])
        self.assertEqual(response.context['president'][1]['candidate'], self.candidates[0])
        self.assertEqual(response.context['president'][1]['votes'], 2)
        self.assertFalse(response.context['president'][1]['tie'])
        self.assertEqual(response.context['vice_president'][0]['candidate'], self.candidates[3])
        self.assertEqual(response.context['vice_president'][0]['votes'], 4)
        self.assertEqual(response.context['vice_president'][1]['candidate'], self.candidates[2])
        self.assertEqual(response.context['vice_president'][1]['votes'], 2)
        self.assertFalse(response.context['vice_president'][1]['tie'])
        self.assertEqual(response.context['secretary'][0]['candidate'], self.candidates[5])
        self.assertEqual(response.context['secretary'][0]['votes'], 5)
        self.assertEqual(response.context['secretary'][1]['candidate'], self.candidates[4])
        self.assertEqual(response.context['secretary'][1]['votes'], 1)
        self.assertEqual(response.context['treasurer'][0]['candidate'], self.candidates[8])
        self.assertEqual(response.context['treasurer'][0]['votes'], 3)
        self.assertEqual(response.context['treasurer'][1]['candidate'], self.candidates[7])
        self.assertEqual(response.context['treasurer'][1]['votes'], 2)
        self.assertEqual(response.context['member_at_large'][0]['candidate'], self.candidates[13])
        self.assertEqual(response.context['member_at_large'][0]['votes'], 6)
        self.assertEqual(response.context['member_at_large'][1]['candidate'], self.candidates[11])
        self.assertEqual(response.context['member_at_large'][1]['votes'], 4)
        self.assertEqual(response.context['member_at_large'][2]['candidate'], self.candidates[9])
        self.assertEqual(response.context['member_at_large'][2]['votes'], 3)
        self.assertTrue(response.context['member_at_large'][4]['tie'])

    def test_election_result_tie(self):
        election = self.make_election()
        election.state = 'closed'
        election.save()

        d = timezone.now().date() + timezone.timedelta(days=3)
        member = Member.objects.create(
            student=self.test_user.student_set.last(),
            expire_date=d,
            level=Level.objects.get(pk=1),
            join_date=d.replace(year=d.year - 1),
            begin_date=d.replace(year=d.year - 3)
        )
        #         pos =      [1,  1,  2,  2,  3,  3,  4,  4,  4,    5,  5,  5,  5,  5]
        #         students = [9, 10, 11, 12, 14, 15, 16, 17, 18,   19, 20, 22, 23, 24]
        #                     0,  1,  2,  3,  4,  5,  6,  7,  8,    9, 10, 11, 12, 13
        self.vote(election, 4, 0, 2, 5, 8, [9, 11, 13])
        self.vote(election, 5, 1, 2, 4, 8, [9, 11, 13])
        self.vote(election, 6, 1, 3, 5, 6, [11, 12, 13])
        self.vote(election, 7, 0, 3, 4, 7, [10, 11])
        self.vote(election, 8, 1, 3, 4, 6, [10, 11, 13])
        self.vote(election, 9, 0, 3, 5, 7, [9, 12, 13])

        response = self.client.get(reverse('membership:election_result', kwargs={'election_id': election.id}),
                                   secure=True)

        self.assertEqual(response.context['president'][0]['votes'], 3)
        self.assertFalse(response.context['president'][0]['tie'])
        self.assertEqual(response.context['president'][1]['votes'], 3)
        self.assertTrue(response.context['president'][1]['tie'])
        self.assertEqual(response.context['vice_president'][0]['candidate'], self.candidates[3])
        self.assertEqual(response.context['vice_president'][0]['votes'], 4)
        self.assertEqual(response.context['vice_president'][1]['candidate'], self.candidates[2])
        self.assertEqual(response.context['vice_president'][1]['votes'], 2)
        self.assertFalse(response.context['vice_president'][1]['tie'])
        self.assertEqual(response.context['secretary'][0]['votes'], 3)
        self.assertEqual(response.context['secretary'][1]['votes'], 3)
        self.assertTrue(response.context['secretary'][1]['tie'])
        self.assertEqual(response.context['treasurer'][0]['votes'], 2)
        self.assertEqual(response.context['treasurer'][1]['votes'], 2)
        self.assertTrue(response.context['treasurer'][1]['tie'])
        self.assertEqual(response.context['member_at_large'][0]['votes'], 5)
        self.assertEqual(response.context['member_at_large'][1]['votes'], 5)
        self.assertTrue(response.context['member_at_large'][1]['tie'])
        self.assertEqual(response.context['member_at_large'][2]['votes'], 3)
        self.assertFalse(response.context['member_at_large'][2]['tie'])

    # @tag('temp')
    def test_election_notification(self):
        election = self.make_election()
        em = EmailMessage()
        em.election_notification(election, False)
        bulk_emails = BulkEmail.objects.all()
        self.assertEqual(bulk_emails.count(), 1)
        self.assertTrue(bulk_emails[0].body.find('We will be having elections on') > 0)
        self.assertTrue(bulk_emails[0].body.find('President: Amanda Cushman, Cathy Rodriguez') > 0)
        self.assertTrue(bulk_emails[0].body.find('Vice President: Brant Applegate, Lee Steen') > 0)
        self.assertTrue(bulk_emails[0].body.find('Secretary: Billie Farquhar, Dorothy Carver') > 0)
        self.assertTrue(bulk_emails[0].body.find('Treasurer: Kevin Lezama, Scott Glidden, Crystal Vanover') > 0)
        self.assertTrue(bulk_emails[0].body.find(
            'Members at Large (select 3): Mark Davis, Dean Flynn, Amanda Jackson, Luther Cole, Jeanette Sheppard') > 0)
        self.assertFalse(
            bulk_emails[0].body.find("Join Zoom Meeting ID: 123 1234 1234\n\nhttps://us02web.zoom.us/j/1231231234") > 0)
        logger.warning(bulk_emails[0].body)

    # @tag('temp')
    def test_election_notification_opened(self):
        election = self.make_election()
        election.state = 'scheduled'
        election.save()
        em = EmailMessage()
        em.election_notification(election, True)
        bulk_emails = BulkEmail.objects.all()
        self.assertEqual(bulk_emails.count(), 1)

        self.assertTrue(bulk_emails[0].body.find('Elections are now open and will close at') > 0)
        self.assertTrue(bulk_emails[0].body.find('President: Amanda Cushman, Cathy Rodriguez') > 0)
        self.assertTrue(bulk_emails[0].body.find('Vice President: Brant Applegate, Lee Steen') > 0)
        self.assertTrue(bulk_emails[0].body.find('Secretary: Billie Farquhar, Dorothy Carver') > 0)
        self.assertTrue(bulk_emails[0].body.find('Treasurer: Kevin Lezama, Scott Glidden, Crystal Vanover') > 0)
        self.assertTrue(bulk_emails[0].body.find(
            'Members at Large (select 3): Mark Davis, Dean Flynn, Amanda Jackson, Luther Cole, Jeanette Sheppard') > 0)
        self.assertTrue(bulk_emails[0].body.find(
            "Join Zoom Meeting ID: 123 1234 1234\n\nhttps://us02web.zoom.us/j/1231231234") > 0)
        logger.warning(bulk_emails[0].body)

    # @tag('temp')
    def test_election_scheduled_notification(self):
        election = self.make_election()
        election.election_date = timezone.now() + timezone.timedelta(days=6, hours=17)
        election.save()

        membership_election_calendar_notify(timezone.now() - timezone.timedelta(days=1))
        bulk_emails = BulkEmail.objects.all()
        self.assertEqual(bulk_emails.count(), 1)