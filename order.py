from abc import ABC, abstractmethod


class Order(ABC):
    # TODO static attributes inheritance
    # TODO add dynamic attribute
    offered = False

    def __init__(self, price, volume, event_sender, event_time):
        self.price = price
        self.volume = volume
        self.remain = volume
        self.event_sender = event_sender
        self.event_time = event_time

    @abstractmethod
    def to_string(self):
        pass
