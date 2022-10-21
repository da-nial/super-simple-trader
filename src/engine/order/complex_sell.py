from engine.order.complex_order import ComplexOrder
from engine.order.sell import Sell


class ComplexSell(ComplexOrder):

    def __init__(self, opening_price, limit_price, amount):
        super().__init__(opening_price, limit_price, amount)
        self.order_name = 'فروش'
        self.order_char = 'ف'
        self.order_verb = 'فروخته شده'
        self.order_today_tomorrow = 'امروزی'

    def is_better_price(self, offer_price):
        return offer_price >= self.limit_price

    def add_to_list(self, offer_price, offer_amount, event_sender, event_time):
        self.simple_orders.append(Sell(offer_price, offer_amount, event_sender, event_time))

    def update_price_for_order_accepted(self):
        self.clear_counter()

    def update_price_for_order_sent(self):
        self.counter += 1
        if self.current_price > self.limit_price:
            if self.counter >= 5:
                self.current_price -= 1
                self.clear_counter()

    def update_price_for_transaction(self, transaction_price):
        if transaction_price >= self.current_price:
            self.current_price = transaction_price
            self.clear_counter()
