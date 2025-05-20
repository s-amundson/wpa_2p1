# This example requires the 'message_content' intent.
import asyncio
import discord
import os
import json
import logging

from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage
from celery import Celery, shared_task
from discord.ext import commands
from datetime import timedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s: %(lineno)d  %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
intents = discord.Intents.default()
intents.message_content = True

# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents)

staff_channel_id = 1353451822538293288

broker = os.environ.get("CELERY_BROKER")

# celery setup
app = Celery('wpa_project', broker=broker, backend='rpc://')

async def main():
    await asyncio.gather(
        start_client(),
        rabbit_receiver()
    )

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    logger.warning(message)
    # logger.warning(message.reference)
    if message.content.startswith('$'):
        await bot.process_commands(message)
        return
    message_dict = {
        'id':message.id,
        'channel': {'id': message.channel.id, 'name': message.channel.name},
        'author': {'id': message.author.id, 'name': message.author.name},
        'content': message.content,
        'reference': message.reference
    }
    logger.warning(message_dict)
    channel = bot.get_channel(staff_channel_id)
    result = app.send_task('discord_bot.tasks.discord_message', args=(json.dumps(message_dict),))
    logger.warning(result.get(timeout=1))
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        await channel.send('got message')
        # await channel.send('staff send')
    # if message.channel.id == staff_channel_id:
    #     result = app.send_task('wpa_project.celery.debug_task')
    #     await message.channel.send(result.get(timeout=1))
    #     # logger.debug(result.get(timeout=1))

@bot.event
async def on_message_edit(before, after):
    # if before.author == bot.user:
    #     return
    logger.warning(after)
    logger.warning(after.content)

@bot.event
async def on_raw_poll_vote_add(payload):
    logger.debug(payload)
    app.send_task('minutes.tasks.poll_vote', args=[payload.channel_id, payload.message_id, payload.user_id, payload.answer_id])

@bot.group(invoke_without_command=True)
async def motion(ctx):
    logger.debug('motion group')
    await ctx.send('use "$motion create" to make a motion. Reply to a poll with "$motion update" to change, '
                   '"$motion end" to end voting, and "$motion cancel" to cancel motion.')

@motion.command(name='cancel')
async def motion_cancel(ctx):
    poll_msg = await motion_end(ctx)
    app.send_task('minutes.tasks.end_motion', args=[ctx.channel.id, ctx.author.id, poll_msg.id, True])

@motion.command(name='create')
async def motion_create(ctx, *, arg):
    logger.debug(ctx.message.id)
    app.send_task('minutes.tasks.create_motion', args=[ctx.channel.id, ctx.author.id, arg, ctx.message.id])

async def motion_end(ctx):
    logger.debug(ctx.message.reference.message_id)
    poll_msg = None
    try:
        poll_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        msg = await poll_msg.end_poll()
        logger.debug(msg)
    except discord.NotFound:
        logger.debug('not found')
    except discord.Forbidden as e:
        logger.debug(f'forbidden {e}')
    except discord.HTTPException as e:
        logger.debug(f'HTTPException {e}')
    except:
        logger.debug('other exception')
    return poll_msg

@motion.command(name='end')
async def motion_end_bot(ctx):
    logger.debug('motion end bot')
    poll_msg = await motion_end(ctx)
    logger.debug(poll_msg)

    app.send_task('minutes.tasks.end_motion',
                  args=[ctx.channel.id, ctx.author.id, ctx.message.reference.message_id, False])


@motion.command(name='update')
async def motion_update(ctx, *, arg):
    logger.debug('motion update')
    poll_msg = await motion_end(ctx)
    result = app.send_task('minutes.tasks.update_motion',
                  args=[ctx.channel.id, ctx.author.id, arg, ctx.message.id, ctx.message.reference.message_id])
    res = result.get(timeout=1)
    logger.warning(res)

@bot.event
async def on_raw_poll_vote_remove(payload):
    logger.debug(payload)

async def process_rabbit_message(
    message: AbstractIncomingMessage,
) -> None:
    async with message.process():
        logger.debug(message.body)
        await asyncio.sleep(1)
        load = json.loads(message.body)
        logger.debug(load)
        discord_channel = bot.get_channel(load['channel'])
        if load['poll']:
            if load['poll']['message_id'] and load['poll']['state'] == 'closed':
                poll_msg = await discord_channel.fetch_message(load['poll']['message_id'])
                msg = await poll_msg.end_poll()
                logger.debug(msg)

            else:
                poll = discord.Poll(load['message'], duration=timedelta(hours=load['poll']['duration']))
                for c in load['poll']['choices']:
                    poll.add_answer(text=c)
                if load['poll']['reference_id'] is not None:
                    ref_message = await discord_channel.fetch_message(load['poll']['reference_id'])
                    msg = await discord_channel.send(poll=poll, reference=ref_message)
                else:
                    msg = await discord_channel.send(poll=poll)
                app.send_task('minutes.tasks.confirm_poll', args=[load['poll']['id'], msg.id])
        # else:
        #     msg = await discord_channel.send(load['message'])
        # logger.debug(msg.id)

async def rabbit_receiver() -> None:
    connection = await connect_robust(broker,)

    queue_name = "discord_bot"

    # Creating channel
    channel = await connection.channel()

    # Maximum message count which will be processing at the same time.
    await channel.set_qos(prefetch_count=100)

    # Declaring queue
    # queue = await channel.declare_queue(queue_name, auto_delete=True)
    queue = await channel.declare_queue(queue_name, durable=True)
    # try:
    #     queue = await channel.get_queue(queue_name)
    # except ChannelNotFoundEntity:
    #     queue = await channel.declare_queue(queue_name, durable=True)

    await queue.consume(process_rabbit_message)

    try:
        # Wait until terminate
        await asyncio.Future()
    finally:
        await connection.close()


async def start_client():
    await bot.start(os.environ.get('DISCORD_BOT_TOKEN'))

@bot.command()
async def status(ctx):
    logger.warning('status')
    result = app.send_task('program_app.tasks.get_class_status')
    res = result.get(timeout=1)
    logger.warning(res)
    await ctx.send(res)

@bot.command()
async def test(ctx, arg):
    logger.warning('test')
    logger.warning(ctx.message.id)
    await ctx.send(arg)

if __name__ == '__main__':
    # asyncio.create_task(client.run(os.environ.get('DISCORD_BOT_TOKEN')))
    asyncio.run(main())
