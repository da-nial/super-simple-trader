import asyncio
import os

from src.telegram_bot import SmartTelegramBot, SmartTelegramClient

import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

if __name__ == '__main__':
    SESSION = os.environ.get('TG_SESSION', 'interactive')
    API_ID = os.getenv('TG_API_ID', 'REDACTED')
    API_HASH = os.getenv('TG_API_HASH', 'REDACTED')
    bot_token = os.getenv('TG_BOT_TOKEN', 'REDACTED')

    client = SmartTelegramClient('Danial', API_ID, API_HASH)
    bot = SmartTelegramBot(bot_token=bot_token, telegram_client=client)

    loop = asyncio.get_event_loop()
    task1 = loop.create_task(client.run())
    task2 = loop.create_task(bot.polling(loop=loop))
    loop.run_until_complete(asyncio.wait([task1, task2]))
    loop.close()
