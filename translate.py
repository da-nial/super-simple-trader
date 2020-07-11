import re

from datetime import datetime
from helper import ar_to_en_num


class Translate:
    """" A class to Translate and get needed information from
     different kinds of offers, counter-offers and transfer_rules.
     """

    @staticmethod
    def order(text):
        """" Gets an order instuction as a text, Extracts needed information and returns it as a dictionary.
         :param text: the instruction that is supposed to be translated
         :returns a dictionary that contains price_limit, amount and type of order
         :returns None if the pattern of an order instruction is not found.
         """

        obj = re.fullmatch('^(\d+)(\s*)([خف])(\s*)(ف?)(\s*)(\d+)(\s*)(ت)?(تا)?(\s*)(یج|یجا)?', text)

        if obj is not None:
            if obj.group(3) == "ف":
                op = 'sell'
            elif obj.group(3) == 'خ':
                op = 'buy'

            if obj.group(5) == 'ف':
                today_tomorrow = 'tomorrow'
            else:
                today_tomorrow = 'today'

            if (obj.group(12) == 'یجا'):
                dividable = False
                print('here')
            else:
                print('there')
                dividable = True
            ret = {'price': int(obj.group(1)),
                   'op': op,
                   'today_tomorrow': today_tomorrow,
                   'amount': int(obj.group(7)),
                   'dividable': dividable}
            return ret
        else:
            return None

    @staticmethod
    def order_counter_offer(text):
        """" Gets an order_counter_offer instruction as a text, Extracts needed information and returns it as a dictionary.
         :param text: the counter-offer instruction that is supposed to be translated
         :returns a dictionary that contains amount of counter-offer
         :returns None if the pattern of an order counter-offer is not found.
         """
        obj = re.fullmatch("(ب*)(\s*)(\d+)(\s*)(ب*)", text)

        if obj is not None:
            return int(obj.group(3))
        else:
            return None

    @staticmethod
    def get_prices(text):

        obj = re.fullmatch('^(\d+)(\s+)(\d+)', text)

        if obj is not None:
            prices = text.split()
            prices = [int(price) for price in prices]
            prices.sort()

            return prices
        else:
            return None

    @staticmethod
    def get_time(text):

        obj = re.fullmatch('^(\d{1,2})(:)(\d{1,2})', text)

        if obj is not None:
            text = ar_to_en_num(text)
            return datetime.strptime(text, "%H:%M").time().replace(second=0, microsecond=0)
        else:
            return None

    @staticmethod
    def complete_accept(text):
        obj = re.fullmatch('^(ب*)$', text)
        if obj is not None:
            return 1
        else:
            return None

# print(Translate.order(input()))
