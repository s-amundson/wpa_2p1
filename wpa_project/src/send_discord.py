import asyncio
import json
import os
import aio_pika

class SendDiscord:
    def __init__(self, channel, message, poll=False, poll_choices=None):
        self.routing_key = 'discord_bot'
        self.payload = json.dumps({
            'channel': channel,
            'message':message,
            'poll': poll,
            'poll_choices': poll_choices
        })
        asyncio.run(self.main())

    async def main(self) -> None:
        connection = await aio_pika.connect_robust(
            os.environ.get("CELERY_BROKER"),
        )

        async with connection:
            channel = await connection.channel()

            await channel.default_exchange.publish(
                aio_pika.Message(body=self.payload.encode()),
                routing_key=self.routing_key,
            )
