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
    # logger.warning(message)
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
    # if message.reference is not None:
    #     message_dict['reference']
    logger.warning(message_dict)
    channel = bot.get_channel(staff_channel_id)
    result = app.send_task('program_app.tasks.discord_message', args=(json.dumps(message_dict),))
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
async def on_raw_poll_vote_add(payload):
    logger.debug(payload)
    # app.send_task('program_app.tasks.discord_message')

@bot.event
async def on_raw_poll_vote_remove(payload):
    logger.debug(payload)

async def process_rabbit_message(
    message: AbstractIncomingMessage,
) -> None:
    async with message.process():
        print(message.body)
        logger.debug(message.body)
        await asyncio.sleep(1)
        load = json.loads(message.body)
        print(load)
        discord_channel = bot.get_channel(load['channel'])
        if load['poll']:
            poll = discord.Poll(load['message'], duration=timedelta(hours=1))
            for c in load['poll_choices']:
                poll.add_answer(text=c)
            msg = await discord_channel.send(poll=poll)
        else:
            msg = await discord_channel.send(load['message'])
        logger.debug(msg.id)

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
    await ctx.send(arg)

if __name__ == '__main__':
    # asyncio.create_task(client.run(os.environ.get('DISCORD_BOT_TOKEN')))
    asyncio.run(main())
