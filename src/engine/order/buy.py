from engine.order.order import Order


class Buy(Order):
    def __init__(self, price, volume, event_sender, event_time):
        super().__init__(price, volume, event_sender, event_time)

    def to_string(self):
        buy_report = str(self.price) + 'خ' + str(self.volume) + '\n'
        buy_report += 'فروشنده: ' + self.event_sender + '\n'
        buy_report += 'زمان: ' + self.event_time
        buy_report += '\n__________________________\n'
        return buy_report
