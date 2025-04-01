from aiogram.utils.keyboard import InlineKeyboardBuilder

def categories_keyboard(categories: list[str]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category, callback_data=f"category_{category}")
    builder.adjust(2)
    return builder.as_markup()
