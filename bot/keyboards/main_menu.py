from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Добавить доход")
    builder.button(text="Добавить расход")
    builder.button(text="История транзакций")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
