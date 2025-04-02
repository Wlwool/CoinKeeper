from aiogram.utils.keyboard import ReplyKeyboardBuilder

def categories_keyboard(categories: list[str]):
    builder = ReplyKeyboardBuilder()
    for category in categories:
        builder.button(text=category)
    builder.button(text="Отменить")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
