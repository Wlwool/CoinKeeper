from aiogram.utils.keyboard import ReplyKeyboardBuilder


def cancel_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отменить")
    return builder.as_markup(resize_keyboard=True)
