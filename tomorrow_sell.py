from order import Order


class TomorrowSell(Order):
    def __init__(self, price, volume, event_sender, event_time):
        super().__init__(price, volume, event_sender, event_time)

    def to_string(self):
        sell_report = str(self.price) + 'ف ف' + str(self.volume) + '\n'
        sell_report += 'خریدار: ' + self.event_sender + '\n'
        sell_report += 'زمان: ' + self.event_time
        sell_report += '\n__________________________\n'
        return sell_report
