# Create your tasks here
from celery import shared_task

from discord_bot.models import DiscordChannel
from .models import Poll, PollVote, PollChoices, PollType
from student_app.models import User

import logging
logger = logging.getLogger('minutes')
from celery.utils.log import get_task_logger
celery_logger = get_task_logger('minutes')


@shared_task
def close_poll(poll_id):
    poll = Poll.objects.get(pk=poll_id)
    poll.state = 'closed'
    poll.save()
    poll.to_discord()

@shared_task
def confirm_poll(poll_id, message_id):
    poll = Poll.objects.get(pk=poll_id)
    poll.discord_message = message_id
    celery_logger.debug(message_id)
    poll.save()

@shared_task
def create_motion(channel, discord_user, message, message_id):
    logger.debug(f'create motion channel {channel}, user {discord_user}, {message}')
    user = User.objects.filter(discord_user=discord_user).last()
    chan = DiscordChannel.objects.filter(channel=channel).last()
    logger.debug(f'user {user}, chan {chan}, level {chan.level}')
    if user is None or chan is None:
        return
    if chan.level == 'board' and user.is_board:
        logger.debug('here')
        poll = Poll.objects.create(
            poll_type=PollType.objects.get(poll_type='motion'),
            description=message,
            level='board',
            is_anonymous=False,
            state = 'open',
            duration = 24
        )
        poll.poll_choices.set(PollChoices.objects.all().order_by('id')[:3])
        logger.debug(poll)
        poll.to_discord(message_id)

@shared_task
def end_motion(channel, discord_user, message_id, cancel):
    celery_logger.debug('end motion')
    poll = Poll.objects.filter(discord_message=message_id).last()
    user = User.objects.filter(discord_user=discord_user).last()
    chan = DiscordChannel.objects.filter(channel=channel).last()

    if poll is None or user is None or chan is None:
        return
    if chan.level == 'board' and user.is_board and poll.state == 'open':
        if cancel:
            poll.state = 'canceled'
        else:
            poll.state = 'closed'
        poll.save()

def make_vote(user, poll, answer_id):
    vote, _ = PollVote.objects.update_or_create(
        poll=poll, user=user, defaults={'choice':poll.poll_choices.all().order_by('id')[answer_id - 1]}
    )
    return vote

@shared_task
def poll_vote(channel, message_id, discord_user, answer_id):
    celery_logger.debug(message_id)
    poll = Poll.objects.get(discord_message=message_id)
    user = User.objects.get(discord_user=discord_user)
    if poll is None or user is None:
        return
    celery_logger.debug(poll.state)
    if poll.state == 'open':
        if poll.level == 'board' and user.is_board:
            vote = make_vote(user, poll, answer_id)
            celery_logger.debug(vote.choice)


@shared_task(bind=True)
def update_motion(self, channel, discord_user, message, message_id, reference_id):
    celery_logger.debug('update_motion')
    celery_logger.debug(reference_id)
    poll = Poll.objects.get(discord_message=reference_id)
    if poll is None:
        return {'status': 'Not Found'}
    user = User.objects.filter(discord_user=discord_user).last()
    chan = DiscordChannel.objects.filter(channel=channel).last()
    logger.debug(f'user {user}, chan {chan}, level {chan.level}')
    if user is None or chan is None:
        return {'status': 'Not Authorized'}
    if chan.level == 'board' and user.is_board and poll.state == 'open':
        poll.description = message
        poll.discord_message = message_id
        poll.save()
        PollVote.objects.filter(poll=poll).delete()
        poll.to_discord(message_id)
    return {'status': 'success'}