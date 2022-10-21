import asyncio
import sys

from datetime import datetime

from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import SessionPasswordNeededError
from telethon.network import ConnectionTcpAbridged
# import logging
# logging.basicConfig(level=logging.DEBUG)

from utils.helper import print_title, utc_to_local

from getpass import getpass

from engine.account import Account
from engine.translate import Translate

from engine.order.complex_buy import ComplexBuy
from engine.order.complex_tomorrow_buy import ComplexTomorrowBuy
from engine.order.complex_tomorrow_sell import ComplexTomorrowSell
from engine.order.complex_sell import ComplexSell

# TODO use the loop from our Main Class, pass  it as an argument to the constructor
# Create a global variable to hold the loop we will be using
loop = asyncio.get_event_loop()


async def async_input(prompt):
    """
    Python's ``input()`` is blocking, which means the event loop we set
    above can't be running while we're blocking there. This method will
    let the loop run while we wait for input.
    """
    print(prompt, end='', flush=True)
    return (await loop.run_in_executor(None, sys.stdin.readline)).rstrip()


class SmartTelegramClient(TelegramClient):
    """"" Smart Telegram Client, meant to be used with SmartTelegramClientBot, to send and recieve messages,
    with respect to the given rules
    rules can be devided to three categories, "buy or sell", "today_tomorrow" and finally "transfer"
    the rules can be specified by the user by interacting with the SmartTelegramClientBot.
    Each Rule can be approached in two ways. More Explanation will follow.
    """

    def __init__(self, session_user_id, api_id, api_hash, proxy=None):
        """"" Initializes the SmartTelegramClient
        :param session_used_id: Name of the *.session file
        :param api_id: Telegram's api_id acquired through my.telegram.org.
        :param api_hash: Telegram's api_hash.
        :param proxy: Optional proxy tuple/dictionary.
        """

        print_title('Initialization')

        # The first step is to initialize the TelegramClient, as we are
        # subclassing it, we need to call super().__init__(). On a more
        # normal case you would want 'client = TelegramClient(...)'
        super().__init__(
            session_user_id, api_id, api_hash,
            connection=ConnectionTcpAbridged,
            # If you're using a proxy, set it here.
            proxy=proxy
        )

        # Calling .connect() may raise a connection error False, so you need
        # to except those before continuing. Otherwise you may want to retry
        # as done here.
        print('Connecting to Telegram servers...')
        try:
            loop.run_until_complete(self.connect())
            print('Connected Successfully')
        except IOError:
            # We handle IOError and not ConnectionError because
            # PySocks' errors do not subclass ConnectionError
            # (so this will work with and without proxies).
            print('Initial connection failed. Retrying...')
            loop.run_until_complete(self.connect())

        # If the user hasn't called .sign_in() or .sign_up() yet, they won't
        # be authorized. The first thing you must do is authorize. Calling
        # .sign_in() should only be done once as the information is saved on
        # the *.session file so you don't need to enter the code every time.
        if not loop.run_until_complete(self.is_user_authorized()):
            print('First run. Sending code request...')
            user_phone = input('Enter your phone: ')
            loop.run_until_complete(self.sign_in(user_phone))

            self_user = None
            while self_user is None:
                code = input('Enter the code you just received: ')
                try:
                    self_user = loop.run_until_complete(self.sign_in(code=code))

                # Two-step verification may be enabled, and .sign_in will
                # raise this error. If that's the case ask for the password.
                # Note that getpass() may not work on PyCharm due to a bug,
                # if that's the case simply change it for input().
                except SessionPasswordNeededError:
                    pw = getpass('Two step verification is enabled. '
                                 'Please enter your password: ')

                    self_user = loop.run_until_complete(self.sign_in(password=pw))

        self.chats = None
        self.chat_entities = None

        self.account = Account()

    async def run(self):
        """"" Main Loop of the TelegramClient, LOOOOP!"""
        await self.send_message(entity='me', message='SmartReplier Sent this message to test it self!')

        # Once everything is ready, we can add an event handler.
        #
        # Events are an abstraction over Telegram's "Updates" and
        # are much easier to use.

        await self.get_dialogs()
        self.chats = [351385828, 475598943, 496502212]  # Danial alone 227952
        # self.chats = [365950614, 431639427]  # Danial, Ali and Alireza
        self.chat_entities = []
        for chat in self.chats:
            self.chat_entities.append(await self.get_input_entity(chat))
        self.add_event_handler(self.message_handler,
                               events.NewMessage(chats=self.chat_entities, incoming=True))

        while True:
            print('periodic')
            await asyncio.sleep(10)

            if self.account.has_active_order():
                if self.account.get_last_order().last_offered_time is None or \
                        self.account.get_last_order().last_offered_time != datetime.now().minute:
                    # send_message with the current price and remaining volume order!
                    sent_event_ids = await self.send_to_multiple(chats=self.chats,
                                                                 message=self.account.get_last_order().get_remain_instruction())
                    self.account.get_last_order().last_offered_event_ids = sent_event_ids

                    self.account.get_last_order().last_offered_time = datetime.now().minute
                    print(self.account.get_last_order().last_offered_time)

    async def message_handler(self, event):
        """Callback method for received events.NewMessage

         Note that message_handler is called when a Telegram update occurs
        # and an event is created. Telegram may not always send information
        # about the ``.sender`` or the ``.chat``, so if you *really* want it
        # you should use ``get_chat()`` and ``get_sender()`` while working
        # with events. Since they are methods, you know they may make an API
        # call, which can be expensive.
        """
        print(event)

        event_sender = await (event.get_sender())
        event_sender = self.event_sender_to_string(event_sender)
        event_time = str(utc_to_local(event.message.date).time())

        if self.account.has_active_order():
            offer_dic = Translate.order(event.text)
            counter_offer_amount = Translate.order_counter_offer(event.text)

            if self.does_offer_match(offer_dic):
                check_offer_result = self.account.get_last_order().check_offer(offer_dic['price'], offer_dic['amount'],
                                                                               offer_dic['dividable'], event_sender,
                                                                               event_time)
                if check_offer_result is not None:  # if it is not none then we are going to buy or sell
                    if check_offer_result == -1:
                        rep = await event.reply('ب')
                        await self.send_message(entity='me', message='یک معامله انجام شد')
                        await event.forward_to(entity='me')
                        await rep.forward_to(entity='me')
                    else:
                        await event.reply(str(check_offer_result))
                    await self.fire_changes()

            elif event.reply_to_msg_id in self.account.get_last_order().last_offered_event_ids:
                if counter_offer_amount is not None:
                    self.account.get_last_order().amounted_accept(counter_offer_amount, event_sender, event_time)
                    await self.fire_changes()

                elif event.text == 'ب':
                    self.account.get_last_order().complete_accept(event_sender, event_time)
                    await self.fire_changes()

        elif self.account.is_transfer_active():
            self.account.transfer.set_time(utc_to_local(event.message.date).time().minute)
            if (Translate.order(event.text) is not None):
                offer = Translate.order(event.text)
                if (offer['dividable'] == True):
                    print(offer)
                    offer.update({'time': event_time, 'id': event})
                    response = self.account.transfer.new_offer(offer)
                if response is not None:
                    current_reply = await event.reply(response['current_answer'])
                    older_reply = await response['event'].reply(response['older_answer'])
                    await self.send_message(entity='me', message='یک جا به جایی انجام شد')
                    await response['event'].forward_to(entity='me')
                    await older_reply.forward_to(entity='me')
                    await event.forward_to(entity='me')
                    await current_reply.forward_to(entity='me')

            elif Translate.complete_accept(event.text) is not None:
                if event.is_reply:
                    replied = await event.get_reply_message()
                    self.account.transfer.delete_offer_with_id(replied.id)
            elif Translate.order_counter_offer(event.text) is not None:
                counter = Translate.order_counter_offer(event.text)
                if event.is_reply:
                    replied = await event.get_reply_message()
                    self.account.transfer.modify_offer_with_id(replied.id, counter)

            elif event.text == 'ن':
                self.account.transfer.delete_offer_with_sender_id(event.from_id)
            print(self.account.transfer.sell_list)
            print(self.account.transfer.buy_list)
            print(self.account.transfer.tomorrow_buy_list)
            print(self.account.transfer.tomorrow_sell_list)

    async def fire_changes(self):

        # event_chat = await event.get_chat()
        # other_chats = self.chats.copy()
        # other_chats.remove(event_chat)

        await self.send_to_multiple(chats=self.chats,
                                    message='ن')
        if self.account.has_active_order():
            sent_event_ids = await self.send_to_multiple(chats=self.chats,
                                                         message=self.account.get_last_order().get_remain_instruction())
            self.account.get_last_order().last_offered_event_ids = sent_event_ids
            print('sent_messages_ids: ' + str(sent_event_ids))

    async def send_to_multiple(self, chats, message):
        sent_event_ids = []
        for chat_i in chats:
            sent_event_i = await self.send_message(entity=chat_i, message=message)
            sent_event_ids.append(sent_event_i.id)
        return sent_event_ids

    def does_offer_match(self, offer_dic):  # Checks to see if the offer matches our user's order

        is_matched = False

        if offer_dic is not None:

            if offer_dic['op'] == 'buy' and offer_dic['today_tomorrow'] == 'today':
                if isinstance(self.account.get_last_order(), ComplexSell):
                    is_matched = True

            elif offer_dic['op'] == 'sell' and offer_dic['today_tomorrow'] == 'today':
                if isinstance(self.account.get_last_order(), ComplexBuy):
                    is_matched = True

            elif offer_dic['op'] == 'buy' and offer_dic['today_tomorrow'] == 'tomorrow':
                if isinstance(self.account.get_last_order(), ComplexTomorrowSell):
                    is_matched = True

            elif offer_dic['op'] == 'sell' and offer_dic['today_tomorrow'] == 'tomorrow':
                if isinstance(self.account.get_last_order(), ComplexTomorrowBuy):
                    is_matched = True

        return is_matched

    @staticmethod
    def event_sender_to_string(event_sender):
        event_sender_string = ''
        if event_sender.first_name is None and event_sender.last_name is None:
            event_sender_string = 'بی‌نام!'
        if event_sender.first_name is not None:
            event_sender_string += event_sender.first_name + ' '
        if event_sender.last_name is not None:
            event_sender_string += event_sender.last_name

        return event_sender_string

    async def cancel_order(self):
        response = self.account.cancel_order()
        if response == 0:
            await self.fire_changes()
        return response
