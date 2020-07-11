import asyncio
import os
import telegram_bot

from helper import sprint, print_title, get_env
from telegram_client import SmartTelegramClient

import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)


if __name__ == '__main__':
    SESSION = os.environ.get('TG_SESSION', 'interactive')
    API_ID = get_env('TG_API_ID', 'Enter your API ID: ', int)
    API_HASH = get_env('TG_API_HASH', 'Enter your API hash: ')
    bot_token = get_env('TG_BOT_TOKEN', 'Enter Bot Token: ')

    client = SmartTelegramClient(SESSION, API_ID, API_HASH)
    bot = telegram_bot.SmartTelegramBot(bot_token=bot_token, telegram_client=client)

    loop = asyncio.get_event_loop()
    task1 = loop.create_task(client.run())
    task2 = loop.create_task(bot.polling(loop=loop))
    loop.run_until_complete(asyncio.wait([task1, task2]))
    loop.close()
