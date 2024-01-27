from django import template
import logging
logger = logging.getLogger(__name__)

register = template.Library()

@register.simple_tag
def vote_again(reimbursement, user):
    votes = reimbursement.reimbursementvote_set.filter(student=user.student_set.last())
    if votes.count():
        return 'again'
    return ''


@register.simple_tag
def voter_status(reimbursement, user):
    votes = reimbursement.reimbursementvote_set.filter(student=user.student_set.last())
    if votes.count():
        if votes.last().approve:
            return f'Last Vote: Approve'
        return 'Last Vote: Deny'
    return "Have not Voted"


@register.simple_tag
def vote_counts(reimbursement):
    votes = reimbursement.reimbursementvote_set.all()
    approved = votes.filter(approve=True).count()
    denied = votes.filter(approve=False).count()

    return f'Votes: {approved} approved, {denied} denied'
