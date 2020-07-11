import os
from helper import get_env

from aiogram import Bot, types

from aiogram.dispatcher import Dispatcher, filters
from aiogram.utils import executor
from aiogram.utils.executor import start_webhook

from urllib.parse import urljoin

from telegram_client import SmartTelegramClient

import keyboards

from translate import Translate

from bot_states import BotStates

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from datetime import datetime, time

from helper import is_time_between

PORT = int(os.environ.get('PORT', 5000))


class SmartTelegramBot:
    """ This class wraps telegram bot instance,
     to use it as an instance in the other modules.
    """

    def __init__(self, bot_token, telegram_client: SmartTelegramClient):
        """ __init simply calls constructor of aiogram.Bot(),
        with the token provided as an argument,
        telegram_client is passed as well, so that bot would have access to the clients account
        and would be able to add or remove orders,
         get reports, change transfer rules, change preferences, etc
         :param bot_token: Bots Token provided by botfather
         :param telegram_client: The SmartTelegramClient instance which bot is supposed to control
        """

        # webhook settings
        self.WEBHOOK_HOST = 'https://smart-replier-staging.herokuapp.com'
        self.WEBHOOK_PATH = '/webhook/' + os.environ.get('TG_BOT_TOKEN')
        self.WEBHOOK_URL = urljoin(self.WEBHOOK_HOST, self.WEBHOOK_PATH)

        self.WEBAPP_HOST = '0.0.0.0'
        self.WEBAPP_PORT = os.environ.get('PORT')

        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher(bot=self.bot, storage=MemoryStorage())
        self.dp.middleware.setup(LoggingMiddleware())

        self.client = telegram_client

        self.order_type = None
        self.order_amount = None
        self.order_opening_price = None
        self.order_limit_price = None
        self.order_today_tomorrow = None

        # only allowed_ids can access inner_states
        # self.allowed_ids = [550379443, 167539602, 760034850]
        self.inner_states = BotStates.DEFAULT or \
                            BotStates.ENTER_TYPE or BotStates.ENTER_AMOUNT or \
                            BotStates.ENTER_PRICE or BotStates.ENTER_TODAY_TOMORROW or \
                            BotStates.SEARCH_MODE or BotStates.TRANSFER_MODE

        # TODO OPENING_TIME and CHECK_OUT_TIME should be written to a file!
        self.OPENING_TIME = time(10, 0)
        self.CHECK_OUT_TIME = time(13, 15)

        # General Buttons ==============================================================

        @self.dp.message_handler(commands=['start'], state='*')
        async def start_cmd(message: types.Message):
            # sender = message.from_user['id']
            # if sender not in self.allowed_ids:
            #     await message.reply("403! ACCESS FORBIDDEN!")
            #     await BotStates.PERMISSION_DENIED.set()
            # else:
            await message.reply("خوش آمدید!", reply_markup=keyboards.main_kb)
            await BotStates.DEFAULT.set()

        @self.dp.message_handler(commands=['help'], state=self.inner_states)
        @self.dp.message_handler(lambda msg: msg.text == 'بازگشت', state=self.inner_states)
        @self.dp.message_handler(lambda msg: msg.text == 'بازگشت', state=BotStates.ENTER_TYPE)
        @self.dp.message_handler(lambda msg: msg.text == 'بازگشت', state=BotStates.ENTER_AMOUNT)
        @self.dp.message_handler(lambda msg: msg.text == 'بازگشت', state=BotStates.ENTER_PRICE)
        @self.dp.message_handler(lambda msg: msg.text == 'بازگشت', state=BotStates.ENTER_TODAY_TOMORROW)
        @self.dp.message_handler(lambda msg: msg.text == 'بازگشت', state=BotStates.TRANSFER)
        @self.dp.message_handler(lambda msg: msg.text == 'بازگشت', state=BotStates.CHANGE_OPENING)
        @self.dp.message_handler(lambda msg: msg.text == 'بازگشت', state=BotStates.CHANGE_CHECKOUT)
        async def help_cmd(message: types.Message):
            if not self.is_order_none():
                self.order_clear()

            reply_message = self.client.account.account_status() + '\n' + self.settings_review() + 'دستور خود را وارد کنید.'
            await message.reply(reply_message, reply_markup=keyboards.main_kb)
            await BotStates.DEFAULT.set()

        # Buy and Sell Buttons ========================================================

        @self.dp.message_handler(lambda msg: msg.text == 'خرید و فروش', state=BotStates.DEFAULT)
        async def check_existing_order(message: types.Message):
            if self.client.account.has_active_order():
                reply_message = 'شما یک سفارش ناتمام دارید. \n سفارش مورد نظر:\n'
                reply_message += self.client.account.get_last_order().short_report()
                await message.reply(reply_message, reply_markup=keyboards.order_active_kb)
            else:
                reply_message = 'سفارش فعالی وجود ندارد. '
                await message.reply(reply_message, reply_markup=keyboards.order_inactive_kb)

        @self.dp.message_handler(lambda msg: msg.text == 'ایجاد سفارش جدید', state=BotStates.DEFAULT)
        @self.dp.message_handler(lambda msg: msg.text == 'رها کردن سفارش قبلی و ایجاد سفارش جدید',
                                 state=BotStates.DEFAULT)
        async def ready_for_new_order(message: types.Message):
            # TODO cancel_order should send NUN if needed!
            response = await self.client.cancel_order()
            if response == 0:
                await message.reply('سفارش با موفقیت کنسل شد.')
            reply_message = '❕ نوع سفارش را وارد کنید.'
            await message.reply(reply_message, reply_markup=keyboards.order_type_kb)
            await BotStates.ENTER_TYPE.set()

        @self.dp.message_handler(state=BotStates.ENTER_TYPE)
        async def add_order_type(message: types.Message):
            if message.text == 'خرید':
                self.order_type = 'buy'
            elif message.text == 'فروش':
                self.order_type = 'sell'

            reply_message = self.order_review()
            reply_message += '❕ مقدار سفارش را وارد کنید.'
            await message.reply(reply_message, reply_markup=keyboards.cancel_kb)
            await BotStates.ENTER_AMOUNT.set()

        @self.dp.message_handler(state=BotStates.ENTER_AMOUNT)
        async def add_order_amount(message: types.Message):
            if str(message.text).isdigit():
                self.order_amount = int(message.text)
                reply_message = self.order_review()
                reply_message += '❕ قیمت شروع و قیمت مرزی را وارد کنید.' + '\n'
                reply_message += '(با فاصله) مثال: ۲۵ ۴۰'
                await message.reply(reply_message, reply_markup=keyboards.cancel_kb)
                await BotStates.ENTER_PRICE.set()
            else:
                await message.reply('مقدار تشخیص داده نشد!', reply_markup=keyboards.cancel_kb)

        @self.dp.message_handler(state=BotStates.ENTER_PRICE)
        async def add_order_price(message: types.Message):

            prices = Translate.get_prices(str(message.text))

            if prices is not None:
                if self.order_type == 'buy':
                    self.order_opening_price = prices[0]
                    self.order_limit_price = prices[1]
                elif self.order_type == 'sell':
                    self.order_opening_price = prices[1]
                    self.order_limit_price = prices[0]

                reply_message = self.order_review()

                if is_time_between(self.OPENING_TIME, self.CHECK_OUT_TIME, datetime.now().time()):
                    reply_message += '❕ امروزی یا فردایی؟'
                    await message.reply(reply_message, reply_markup=keyboards.order_today_tomorrow_kb)
                else:
                    reply_message += 'از ساعت تسویه حساب گذشته است. \nفقط سفارش امروزی ممکن می‌باشد.'
                    await message.reply(reply_message, reply_markup=keyboards.order_today_kb)
                await BotStates.ENTER_TODAY_TOMORROW.set()

            else:
                await message.reply('قیمت‌ها تشخیص داده نشد!', reply_markup=keyboards.cancel_kb)

        @self.dp.message_handler(state=BotStates.ENTER_TODAY_TOMORROW)
        async def add_order_today_tomorrow(message: types.Message):
            if message.text == 'امروزی':
                self.order_today_tomorrow = 'today'
            elif message.text == 'فردایی' and is_time_between(self.OPENING_TIME, self.CHECK_OUT_TIME,
                                                              datetime.now().time()):
                self.order_today_tomorrow = 'tomorrow'

            reply_message = self.order_review()
            self.client.account.new_order(self.order_type, self.order_amount, self.order_opening_price,
                                          self.order_limit_price, self.order_today_tomorrow)
            reply_message += 'سفارش با موفقیت اضافه شد!'
            await message.reply(reply_message, reply_markup=keyboards.cancel_kb)
            await BotStates.DEFAULT.set()

        @self.dp.message_handler(lambda msg: msg.text == 'توقف سفارش', state=self.inner_states)
        async def cancel_order(message: types.Message):
            response = self.client.account.cancel_order()
            if response == 0:
                await message.reply('سفارش با موفقیت کنسل شد.', reply_markup=keyboards.main_kb)
            elif response == -1:
                await message.reply('سفارشی برای کنسل شدن یافت نشد.', reply_markup=keyboards.main_kb)

        # Transfer Buttons ===========================================================

        @self.dp.message_handler(lambda msg: msg.text == 'جابه‌جایی', state=BotStates.DEFAULT)
        async def transfer_cmd(message: types.Message):
            reply_message = 'جابه‌جایی '
            if self.client.account.is_transfer_active():
                reply_message += 'فعال است!' + '\n'
                reply_message += 'دستور خود را وارد کنید'
                await message.reply(reply_message, reply_markup=keyboards.transfer_active_kb)
            else:
                reply_message += 'غیر فعال است!' + '\n'
                reply_message += 'دستور خود را وارد کنید'
                await message.reply(reply_message, reply_markup=keyboards.transfer_inactive_kb)

            await BotStates.TRANSFER.set()

        @self.dp.message_handler(lambda msg: msg.text == 'فعال کردن جابه‌جایی', state=BotStates.TRANSFER)
        async def transfer_turn_on(message: types.Message):

            if (self.client.account.transfer is not None) and (self.client.account.transfer.is_active):
                await message.reply('جابه‌جایی از قبل فعال است!', reply_markup=keyboards.cancel_kb)
            else:
                self.client.account.new_transfer()
                await message.reply('جابه‌جایی با موفقیت فعال شد!', reply_markup=keyboards.cancel_kb)

        @self.dp.message_handler(lambda msg: msg.text == 'غیر فعال کردن جابه‌جایی', state=BotStates.TRANSFER)
        async def transfer_turn_off(message: types.Message):
            if not self.client.account.transfer.is_active:
                await message.reply('جابه‌جایی از قبل غیر فعال است!', reply_markup=keyboards.cancel_kb)
            else:
                self.client.account.transfer.turn_off()
                await message.reply('جابه‌جایی با موفقیت غیر فعال شد!', reply_markup=keyboards.cancel_kb)

        # Report Buttons =============================================================

        @self.dp.message_handler(lambda msg: msg.text == 'گزارش', state=self.inner_states)
        async def report(message: types.Message):
            await message.reply('گزارش کدام مورد؟', reply_markup=keyboards.report_kb)

        @self.dp.message_handler(lambda msg: msg.text == 'گزارش خرید و فروش‌ها', state=self.inner_states)
        async def report_order(message: types.Message):
            await message.reply('شیوه‌ی گزارش‌دهی را انتخاب کنید', reply_markup=keyboards.report_order_kb)

        @self.dp.message_handler(lambda msg: msg.text == '۵ سفارش آخر', state=self.inner_states)
        async def report_last_5(message: types.Message):
            response = self.client.account.orders_report_by_num(5)
            await message.reply(response, reply_markup=keyboards.cancel_kb)

        @self.dp.message_handler(lambda msg: msg.text == 'جست و جو بر اساس سفارش', state=self.inner_states)
        async def report_by_name(message: types.Message):
            await BotStates.SEARCH_MODE.set()
            await message.reply('برای جست و جو شرح سفارش را وارد کنید:', reply_markup=keyboards.cancel_kb)

        @self.dp.message_handler(state=BotStates.SEARCH_MODE)
        async def report_complete(message: types.Message):
            response = self.client.account.orders_report_by_name(message.text)
            await message.reply(response, reply_markup=keyboards.main_kb)
            await BotStates.DEFAULT.set()

        @self.dp.message_handler(lambda msg: msg.text == 'گزارش جابه‌جایی‌ها', state=self.inner_states)
        async def report_transfer(message: types.Message):
            # TODO add transfer report
            await message.reply(self.client.account.transfer_report(), reply_markup=keyboards.cancel_kb)

        # SETTINGS  Buttons =============================================================

        @self.dp.message_handler(lambda msg: msg.text == 'تنظیمات', state=BotStates.DEFAULT)
        async def change_settings(message: types.Message):
            reply_message = self.settings_review()
            reply_message += 'دستور خود را وارد کنید.'
            await message.reply(reply_message, reply_markup=keyboards.settings_kb)

        @self.dp.message_handler(lambda msg: msg.text == 'تغییر ساعت شروع', state=BotStates.DEFAULT)
        async def ready_change_opening(message: types.Message):
            reply_message = self.settings_review()
            reply_message += 'ساعت شروع جدید را وارد کنید. \n(بین ۰ تا ۲۳)'
            reply_message += 'مثال: ' + '10:00'
            await message.reply(reply_message, reply_markup=keyboards.cancel_kb)
            await BotStates.CHANGE_OPENING.set()

        @self.dp.message_handler(lambda msg: msg.text == 'تغییر ساعت تسویه', state=BotStates.DEFAULT)
        async def ready_change_checkout(message: types.Message):
            reply_message = self.settings_review()
            reply_message += 'ساعت تسویه جدید را وارد کنید. \n(بین ۰ تا ۲۳)'
            reply_message += 'مثال: ' + '۱۳:۴۰'
            await message.reply(reply_message, reply_markup=keyboards.cancel_kb)
            await BotStates.CHANGE_CHECKOUT.set()

        @self.dp.message_handler(state=BotStates.CHANGE_OPENING)
        async def change_opening(message: types.Message):
            new_opening = Translate.get_time(message.text)
            if new_opening is not None:
                self.OPENING_TIME = new_opening
                reply_message = 'ساعت شروع با موفقیت تغییر یافت.'
                await message.reply(reply_message, reply_markup=keyboards.cancel_kb)
                await BotStates.DEFAULT.set()

        @self.dp.message_handler(state=BotStates.CHANGE_CHECKOUT)
        async def change_checkout(message: types.Message):
            new_checkout = Translate.get_time(message.text)
            if new_checkout is not None:
                self.CHECK_OUT_TIME = new_checkout
                reply_message = 'ساعت تسویه با موفقیت تغییر یافت.'
                await message.reply(reply_message, reply_markup=keyboards.cancel_kb)
                await BotStates.DEFAULT.set()

    async def on_startup(self, dp):
        """Simple hook for aiohttp application which manages webhook"""
        await self.bot.delete_webhook()
        await self.bot.set_webhook(self.WEBHOOK_URL)

    async def on_shutdown(self, dispatcher: Dispatcher):
        await dispatcher.storage.close()
        await dispatcher.storage.wait_closed()

    def polling(self):
        # executor.start_polling(dispatcher=self.dp,
        #                        skip_updates=True,
        #                        loop=loop,
        #                        on_shutdown=self.shutdown)
        executor.start_webhook(dispatcher=self.dp, webhook_path=self.WEBHOOK_PATH,
                               on_startup=self.on_startup, on_shutdown=self.on_shutdown,
                               host=self.WEBAPP_HOST, port=self.WEBAPP_PORT)

    def order_review(self):
        order_review = '📍 سفارش جدید'
        order_review += '\n'
        order_review += 'نوع: '
        if self.order_type == 'buy':
            order_review += 'خرید'
        elif self.order_type == 'sell':
            order_review += 'فروش'
        order_review += '\n'

        order_review += 'مقدار: '
        if self.order_amount is not None:
            order_review += str(self.order_amount)
        order_review += '\n'

        order_review += 'قیمت شروع: '
        if self.order_opening_price is not None:
            order_review += str(self.order_opening_price)
        order_review += '\n'

        order_review += 'قیمت مرزی: '
        if self.order_limit_price is not None:
            order_review += str(self.order_limit_price)
        order_review += '\n'

        order_review += 'امروزی یا فردایی: '
        if self.order_today_tomorrow == 'today':
            order_review += 'امروزی'
        elif self.order_today_tomorrow == 'tomorrow':
            order_review += 'فردایی'
        order_review += '\n\n'

        return order_review

    def order_clear(self):
        self.order_type = None
        self.order_amount = None
        self.order_opening_price = None
        self.order_limit_price = None
        self.order_today_tomorrow = None

    def is_order_none(self):
        return self.order_type is None and \
               self.order_amount is None and \
               self.order_opening_price is None and \
               self.order_limit_price is None and \
               self.order_today_tomorrow is None

    def settings_review(self):
        settings_review = 'تنظیمات فعلی: ⚙️\n'
        settings_review += 'ساعت شروع معاملات: ' + time.strftime(self.OPENING_TIME, "%H:%M")
        settings_review += '\n'
        settings_review += 'ساعت تسویه حساب: ' + time.strftime(self.CHECK_OUT_TIME, "%H:%M")
        settings_review += '\n\n'
        return settings_review
