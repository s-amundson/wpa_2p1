# This example requires the 'message_content' intent.
import asyncio
import discord
import os
import pika
from celery import Celery, shared_task
from celery.utils.log import get_task_logger
celery_logger = get_task_logger('program_app')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

staff_channel_id = 1353451822538293288

# await channel.send('hello')

# celery setup
app = Celery('wpa_project', broker="amqp://user:password@rabbitmq_dev:5672", backend='rpc://')

# @shared_task
# async def bot_task():
#     print('bot task')
#     # celery_logger.warning('bot task')
#     channel = client.get_channel(staff_channel_id)
#     await channel.send('bot task')
#
# @app.task(bind=True)
# async def bot_task2(self):
#     print('bot task2')
#     # celery_logger.warning('bot task2')
#     channel = client.get_channel(staff_channel_id)
#     await channel.send('bot task2')

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            client.start(os.environ.get('DISCORD_BOT_TOKEN')))
            # client.run(os.environ.get('DISCORD_BOT_TOKEN')))

        task2 = tg.create_task(
            rabbit_receiver())
    # asyncio.create_task()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(message.channel.id)
    celery_logger.warning(message.channel.id)
    channel = client.get_channel(staff_channel_id)
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        await channel.send('got message')
        # await channel.send('staff send')
    if message.channel.id == staff_channel_id:
        result = app.send_task('wpa_project.celery.debug_task')
        await message.channel.send(result.get(timeout=1))

async def rabbit_receiver():
    credentials = pika.PlainCredentials('user', 'password')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq_dev', credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    # asyncio.create_task(client.run(os.environ.get('DISCORD_BOT_TOKEN')))
    asyncio.run(main())
