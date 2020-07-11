from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

cancel_btn = KeyboardButton(text='بازگشت')

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_kb.add(cancel_btn)

# Main menu Keyboard
main_order_btn = KeyboardButton(text='خرید و فروش')
main_transfer_btn = KeyboardButton(text='جابه‌جایی')
main_report_btn = KeyboardButton(text='گزارش')
main_settings_btn = KeyboardButton(text='تنظیمات')

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(main_order_btn)
main_kb.add(main_transfer_btn)
main_kb.add(main_report_btn)
main_kb.add(main_settings_btn)

order_add_anyway_btn = KeyboardButton(text='رها کردن سفارش قبلی و ایجاد سفارش جدید')
order_stop_btn = KeyboardButton(text='توقف سفارش')

order_active_kb = ReplyKeyboardMarkup(resize_keyboard=True)
order_active_kb.add(order_add_anyway_btn)
order_active_kb.add(order_stop_btn)
order_active_kb.add(cancel_btn)

order_add_btn = KeyboardButton(text='ایجاد سفارش جدید')

order_inactive_kb = ReplyKeyboardMarkup(resize_keyboard=True)
order_inactive_kb.add(order_add_btn)
order_inactive_kb.add(cancel_btn)

order_buy_btn = KeyboardButton(text='خرید')
order_sell_btn = KeyboardButton(text='فروش')

order_type_kb = ReplyKeyboardMarkup(resize_keyboard=True)
order_type_kb.add(order_buy_btn)
order_type_kb.add(order_sell_btn)
order_type_kb.add(cancel_btn)

order_today_btn = KeyboardButton(text='امروزی')
order_tomorrow_btn = KeyboardButton(text='فردایی')

order_today_tomorrow_kb = ReplyKeyboardMarkup(resize_keyboard=True)
order_today_tomorrow_kb.add(order_today_btn)
order_today_tomorrow_kb.add(order_tomorrow_btn)
order_today_tomorrow_kb.add(cancel_btn)

order_today_kb = ReplyKeyboardMarkup(resize_keyboard=True)
order_today_kb.add(order_today_btn)
order_today_kb.add(cancel_btn)

transfer_turn_off_btn = KeyboardButton('غیر فعال کردن جابه‌جایی')

transfer_active_kb = ReplyKeyboardMarkup(resize_keyboard=True)
transfer_active_kb.add(transfer_turn_off_btn)
transfer_active_kb.add(cancel_btn)

transfer_turn_on_btn = KeyboardButton('فعال کردن جابه‌جایی')

transfer_inactive_kb = ReplyKeyboardMarkup(resize_keyboard=True)
transfer_inactive_kb.add(transfer_turn_on_btn)
transfer_inactive_kb.add(cancel_btn)

report_order = KeyboardButton('گزارش خرید و فروش‌ها')
report_transfer = KeyboardButton('گزارش جابه‌جایی‌ها')

report_kb = ReplyKeyboardMarkup(resize_keyboard=True)
report_kb.add(report_order)
report_kb.add(report_transfer)
report_kb.add(cancel_btn)

report_by_number = KeyboardButton('۵ سفارش آخر')
report_by_instruction = KeyboardButton('جست و جو بر اساس سفارش')

report_order_kb = ReplyKeyboardMarkup(resize_keyboard=True)
report_order_kb.add(report_by_number)
report_order_kb.add(report_by_instruction)
report_order_kb.add(cancel_btn)

settings_opening_change = KeyboardButton('تغییر ساعت شروع')
settings_checkout_change = KeyboardButton('تغییر ساعت تسویه')

settings_kb = ReplyKeyboardMarkup(resize_keyboard=True)
settings_kb.add(settings_opening_change)
settings_kb.add(settings_checkout_change)
settings_kb.add(cancel_btn)
