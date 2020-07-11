from order import Order
from buy import Buy
from sell import Sell
from helper import en_to_ar_num
from translate import Translate


class Transfer:
    def __init__(self):
        self.turn_on()
        self.buy_list = []
        self.sell_list = []
        self.tomorrow_sell_list = []
        self.tomorrow_buy_list = []

    def new_offer(self, offer):
        response = self.match(offer)
        if response is not None:
            matched = response[0]
            if matched['amount'] == offer['amount']:
                ret = {'event': matched['id'], 'current_answer': 'ب', 'older_answer': 'ب'}
                del response[0]
            elif matched['amount'] > offer['amount']:
                ret = {'event': matched['id'], 'current_answer': 'ب', 'older_answer': str(offer['amount'])}
                del response[0]
                matched['amount'] -= offer['amount']
                self.add_an_offer(matched)
            elif matched['amount'] < offer['amount']:
                ret = {'event': matched['id'], 'current_answer': str(matched['amount']), 'older_answer': 'ب'}
                del response[0]
                offer['amount'] -= matched['amount']
                self.new_offer(offer)
            return ret
        else:
            self.add_an_offer(offer)
            return None

    def match(self, offer):
        if offer['op'] == "buy" and offer['today_tomorrow'] == 'tomorrow':
            if (self.tomorrow_sell_list) and (self.tomorrow_sell_list[0]['price'] <= offer['price']):
                return self.tomorrow_sell_list
            else:
                return None
        elif offer['op'] == "buy" and offer['today_tomorrow'] == 'today':
            if (self.sell_list) and (self.sell_list[0]['price'] <= offer['price']):
                return self.sell_list
            else:
                return None
        elif offer['op'] == "sell" and offer['today_tomorrow'] == 'tomorrow':
            if (self.tomorrow_buy_list) and (self.tomorrow_buy_list[0]['price'] >= offer['price']):
                return self.tomorrow_buy_list
            else:
                return None
        elif offer['op'] == "sell" and offer['today_tomorrow'] == 'today':
            if (self.buy_list) and (self.buy_list[0]['price'] >= offer['price']):
                return self.buy_list
            else:
                return None

    def add_an_offer(self, offer):
        if offer['op'] == "buy" and offer['today_tomorrow'] == 'tomorrow':
            self.add_to_tomorrow_buy(offer)
        elif offer['op'] == "buy" and offer['today_tomorrow'] == 'today':
            self.add_to_buy(offer)
        elif offer['op'] == "sell" and offer['today_tomorrow'] == 'tomorrow':
            self.add_to_tomorrow_sell(offer)
        elif offer['op'] == "sell" and offer['today_tomorrow'] == 'today':
            self.add_to_sell(offer)

    def add_to_tomorrow_buy(self, offer):
        ctr = 0
        for x in self.tomorrow_buy_list:
            if (x['price'] < offer['price']) or (x['price'] == offer['price'] and x['amount'] < offer['amount']):
                self.tomorrow_buy_list.insert(ctr, offer)
                return
            ctr += 1
        self.tomorrow_buy_list.append(offer)

    def add_to_buy(self, offer):
        ctr = 0
        for x in self.buy_list:
            if (x['price'] < offer['price']) or (x['price'] == offer['price'] and x['amount'] < offer['amount']):
                self.buy_list.insert(ctr, offer)
                return
            ctr += 1
        self.buy_list.append(offer)

    def add_to_sell(self, offer):
        ctr = 0
        for x in self.sell_list:
            if (x['price'] > offer['price']) or (x['price'] == offer['price'] and x['amount'] < offer['amount']):
                self.sell_list.insert(ctr, offer)
                return
            ctr += 1
        self.sell_list.append(offer)

    def add_to_tomorrow_sell(self, offer):
        ctr = 0
        for x in self.tomorrow_sell_list:
            if (x['price'] > offer['price']) or (x['price'] == offer['price'] and x['amount'] < offer['amount']):
                self.tomorrow_sell_list.insert(ctr, offer)
                return
            ctr += 1
        self.tomorrow_sell_list.append(offer)

    def delete_offer_with_id(self, id):
        for x in self.buy_list:
            if x['id'].id == id:
                self.buy_list.remove(x)

        for x in self.sell_list:
            if x['id'].id == id:
                self.sell_list.remove(x)

        for x in self.tomorrow_buy_list:
            if x['id'].id == id:
                self.tomorrow_buy_list.remove(x)

        for x in self.tomorrow_sell_list:
            if x['id'].id == id:
                self.tomorrow_sell_list.remove(x)

    def modify_offer_with_id(self, id, counter):
        for x in self.sell_list:
            if x['id'].id == id:
                if x['amount'] > counter:
                    x['amount'] -= counter
                    offer = x
                    self.sell_list.remove(x)
                    self.add_to_sell(offer)
                else:
                    self.sell_list.remove(x)
        for x in self.buy_list:
            if x['id'].id == id:
                if x['amount'] > counter:
                    x['amount'] -= counter
                    offer = x
                    self.buy_list.remove(x)
                    self.add_to_buy(offer)
                else:
                    self.buy_list.remove(x)
        for x in self.tomorrow_sell_list:
            if x['id'].id == id:
                if x['amount'] > counter:
                    x['amount'] -= counter
                    offer = x
                    self.tomorrow_sell_list.remove(x)
                    self.add_to_tomorrow_sell(offer)
                else:
                    self.tomorrow_sell_list.remove(x)
        for x in self.tomorrow_buy_list:
            if x['id'].id == id:
                if x['amount'] > counter:
                    x['amount'] -= counter
                    offer = x
                    self.tomorrow_buy_list.remove(x)
                    self.add_to_tomorrow_buy(offer)
                else:
                    self.tomorrow_buy_list.remove(x)

    def delete_offer_with_sender_id(self, id):
        for x in self.sell_list:
            if x['id'].from_id == id:
                self.sell_list.remove(x)

        for x in self.buy_list:
            if x['id'].from_id == id:
                self.buy_list.remove(x)

        for x in self.tomorrow_sell_list:
            if x['id'].from_id == id:
                self.tomorrow_sell_list.remove(x)

        for x in self.tomorrow_buy_list:
            if x['id'].from_id == id:
                self.tomorrow_buy_list.remove(x)

    # To change is_active status of transfer instance =============================================================
    def turn_on(self):
        self.is_active = True

    def turn_off(self):
        self.is_active = False

    # TODO update!
    def report(self):
        transfer_report = 'سود کلی:' + str(self.profit) + '\n'
        for order in self.transfer_list:
            transfer_report += order.to_string()
            transfer_report += '===================\n'
        if len(transfer_report) == 0:
            transfer_report += 'جابه‌جایی‌ای انجام نشده‌است! ❗️'

        return transfer_report
