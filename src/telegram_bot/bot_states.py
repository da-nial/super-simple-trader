from aiogram.dispatcher.filters.state import State, StatesGroup


class BotStates(StatesGroup):
    """
        represents different states of SmartTelegramBot
        NEW_ORDER_LOCKED: the state of adding new orders is locked
        NEW_ORDER_UNLOCKED: adding orders is permitted
        SEARCH_MODE: when the defined regex of ؛۱۵خ۳۰۰ is used to searched in order history
    """
    PERMISSION_DENIED = State()

    DEFAULT = State()

    ENTER_TYPE = State()
    ENTER_AMOUNT = State()
    ENTER_PRICE = State()
    ENTER_TODAY_TOMORROW = State()

    TRANSFER = State()
    SEARCH_MODE = State()

    CHANGE_OPENING = State()
    CHANGE_CHECKOUT = State()
