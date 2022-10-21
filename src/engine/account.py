from engine.translate import Translate
from engine.order.complex_buy import ComplexBuy
from engine.order.complex_sell import ComplexSell
from engine.order.complex_tomorrow_buy import ComplexTomorrowBuy
from engine.order.complex_tomorrow_sell import ComplexTomorrowSell

from engine.transfer import Transfer


class Account:
    def __init__(self):
        self.user_orders = list()

        x = ComplexBuy(0, 0, 0)
        self.user_orders.append(x)
        self.user_orders.remove(x)

        self.transfer = None

    def new_order(self, type, amount, opening_price, limit_price, today_tomorrow):
        if today_tomorrow == 'today':
            if type == 'buy':
                self.user_orders.append(ComplexBuy(opening_price, limit_price, amount))
            elif type == 'sell':
                self.user_orders.append(ComplexSell(opening_price, limit_price, amount))

        elif today_tomorrow == 'tomorrow':
            if type == 'buy':
                self.user_orders.append(ComplexTomorrowBuy(opening_price, limit_price, amount))
            elif type == 'sell':
                self.user_orders.append(ComplexTomorrowSell(opening_price, limit_price, amount))

    def cancel_order(self):
        # TODO cancel_order should send NUN if needed!
        """""
            Cancels the last order of the user_orders, if possible
            if the last order is None or is finished or is already cancelled, nothing will happen and
             -1 will be returned

            :returns 0 if Cancellation is successful
            :returns -1 if Cancellation is not successful!
            """
        if self.get_last_order() is not None and \
                not self.get_last_order().is_done() and \
                not self.get_last_order().is_cancelled:
            self.get_last_order().is_cancelled = True
            return 0
        else:
            return -1

    def get_last_order(self):
        if self.user_orders is not None and \
                len(self.user_orders) > 0:
            return self.user_orders[-1]
        else:
            return None

    def last_order_status(self):
        order_status = 'وضعیت سفارش: '
        if self.has_active_order():
            order_status += '🔵\n' + self.get_last_order().raw_report()
        else:
            order_status += 'سفارش فعالی موجود نیست 🔴'
        order_status += '\n'
        return order_status

    def has_active_order(self):
        # TODO if Buy or sell, in addition to is_done, has active or inactive boolean,
        #  it too should be checked here!
        return self.get_last_order() is not None and \
               not self.get_last_order().is_done() and \
               not self.get_last_order().is_cancelled

    def orders_report_by_num(self, num_go_back):
        return_value = ''
        for order in self.user_orders[-num_go_back:]:
            return_value += order.short_report()

        if not return_value:
            return_value = 'سفارشی یافت نشد! ❗️'

        return return_value

    def orders_report_by_name(self, searched_order):
        searched = Translate.order(searched_order)
        searched_price = searched['price']
        searched_volume = searched['amount']
        return_value = ''
        for order in self.user_orders:
            if order.is_equal(searched_price, searched_volume):
                return_value += order.complete_report()

        if not return_value:
            return_value = 'سفارشی یافت نشد! ❗️'

        return return_value

    def new_transfer(self):
        if self.transfer is None:
            self.transfer = Transfer()
        else:
            self.transfer.turn_on()

    def change_transfer_rule(self, transfer_rule_text):
        translated_transfer_text = Translate.transfer_rule(transfer_rule_text)
        if translated_transfer_text is not None:
            if translated_transfer_text['buy_price_limit'] > translated_transfer_text['sell_price_limit']:
                return -1
            else:
                self.transfer.change_rule(translated_transfer_text['amount_limit'],
                                          translated_transfer_text['buy_price_limit'],
                                          translated_transfer_text['sell_price_limit'])
                return 0
        else:
            return -2

    def is_transfer_active(self):
        return self.transfer is not None and \
               self.transfer.is_active

    def transfer_status(self):
        transfer_status = 'وضعیت جابه‌جایی: \n'

        if (self.transfer is not None) and (self.transfer.is_active):
            transfer_status += 'جابه‌جایی فعال است! 🔵'
        else:
            transfer_status += 'جابه‌جایی غیر فعال است! 🔴'
        transfer_status += '\n'

        return transfer_status

    def transfer_report(self):
        if self.transfer is not None:
            return self.transfer.report()

    def account_status(self):
        return self.last_order_status() + '\n' + self.transfer_status()
