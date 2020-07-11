from abc import ABC, abstractmethod


class ComplexOrder(ABC):
    def __init__(self, opening_price, limit_price, amount):
        self.simple_orders = list()

        self.opening_price = opening_price
        self.limit_price = limit_price

        self.current_price = opening_price
        self.counter = 0

        self.amount = amount

        self.remain = amount
        self.total_cost = 0

        self.last_offered_time = None
        self.last_offered_event_ids = []

        self.is_cancelled = False

        self.order_name = None
        self.order_char = None
        self.order_verb = None
        self.order_today_tomorrow = None

    # updating price every time a transaction has been made,
    # an offer has been accepted or an offer has been sent

    @abstractmethod
    def update_price_for_order_accepted(self):
        pass

    @abstractmethod
    def update_price_for_order_sent(self):
        pass

    @abstractmethod
    def update_price_for_transaction(self, transaction_price):
        pass

    @abstractmethod
    def is_better_price(self, offer_price):
        pass

    @abstractmethod
    def add_to_list(self, offer_price, offer_amount, event_sender, event_time):
        pass

    # TRANSACTIONS ==================================================================

    def check_offer(self, offer_price, offer_amount, offer_dividable, event_sender, event_time):
        """"" Checks an offer to see if it is acceptable
        :param event_sender:
        :param event_time:
        :param offer_price: price of the offer
        :param offer_amount: amount of the offer
        :param offer_dividable: whether an offer is dividable or not, specified with 'یج' or 'یجا'
        :returns  -1 to buy all, a positive number to buy that amount, None to not to buy
        """

        return_value = None

        if self.is_better_price(offer_price):
            if offer_amount <= self.remain:  # buy all
                self.total_cost += offer_amount * offer_price
                self.remain -= offer_amount
                self.add_to_list(offer_price, offer_amount, event_sender, event_time)
                return_value = -1
                self.update_price_for_transaction(offer_price)
            elif offer_dividable:  # buy only remaining amount
                self.total_cost += self.remain * offer_price
                return_value = self.remain
                self.remain = 0
                self.add_to_list(offer_price, offer_amount, event_sender, event_time)
                self.update_price_for_transaction(offer_price)
            else:  # amount is too much and is not dividable, don't buy!
                return_value = None

        else:  # price is too much, don't buy!
            return_value = None

        return return_value

    def amounted_accept(self, amount, event_sender, event_time):
        self.total_cost += self.get_current_price() * int(amount)
        self.remain -= amount
        self.add_to_list(self.get_current_price(), amount, event_sender, event_time)
        self.update_price_for_order_accepted()

    def complete_accept(self, event_sender, event_time):
        if self.remain <= 50:
            self.total_cost += self.remain * self.get_current_price()
            self.remain = 0
            self.add_to_list(self.get_current_price(), self.remain, event_sender, event_time)

        else:
            self.total_cost += 50 * self.limit_price
            self.remain -= 50
            self.add_to_list(self.get_current_price(), 50, event_sender, event_time)
        self.update_price_for_order_accepted()

    # GET INSTRUCTION FOR SENDING OFFERS =======================================

    def get_remain_instruction(self):
        # IMPORTANT! ONLY TO BE USED FOR SENDING OFFER, IT CHANGES CURRENT PRICE!
        remain_instruction = str(self.get_current_price()) + self.order_char
        if self.remain <= 50:
            remain_instruction += str(self.remain)
        else:
            remain_instruction += str(50)
        self.update_price_for_order_sent()
        return remain_instruction

    # REPORTS ==================================================================

    def raw_report(self):

        raw_report = 'نوع: ' + self.order_name + '\n'

        raw_report += 'مقدار: ' + str(self.amount) + '\n'

        raw_report += 'قیمت شروع: ' + str(self.opening_price) + '\n'

        raw_report += 'قیمت مرزی: ' + str(self.limit_price) + '\n'

        raw_report += 'امروزی یا فردایی: ' + str(self.order_today_tomorrow) + '\n'

        raw_report += '\n'

        return raw_report

    def short_report(self):
        return_value = 'سفارش: '
        return_value += self.raw_report() + '\n'
        return_value += self.order_name + ' '
        if self.is_cancelled:
            return_value += 'کنسل شده! ⚠️'
        elif self.is_done():
            return_value += 'کامل شده ✔️'
        else:
            return_value += 'نیمه‌تمام ❗️'
        return_value += '\n'
        return_value += 'مقدار' + self.order_verb + str(self.amount - self.remain) + '\n'

        return_value += 'هزینه‌ی کل: ' + str(self.total_cost)
        return_value += '\n====================\n'
        return return_value

    def complete_report(self):
        return_value = self.short_report()
        for simple_order in self.simple_orders:
            return_value += simple_order.to_string()
        return return_value

    # OTHER METHODS ===========================================================

    def is_equal(self, searched_price, searched_amount):
        return (searched_price == self.limit_price) and \
               (searched_amount == self.amount)

    def get_current_price(self):
        return self.current_price

    def clear_counter(self):
        self.counter = 0

    def is_done(self):
        return self.remain == 0
