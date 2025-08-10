from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="💰 Добавить доход")
    builder.button(text="💸 Добавить расход")
    builder.button(text="📊 История транзакций")
    builder.button(text="🗑 Удалить транзакцию")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

def main_menu_inline_keyboard():
    """Создает inline клавиатуру главного меню для callback-сообщений"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Добавить доход", callback_data="main_add_income")
    builder.button(text="💸 Добавить расход", callback_data="main_add_expense")
    builder.button(text="📊 История транзакций", callback_data="main_history")
    builder.button(text="🗑 Удалить транзакцию", callback_data="main_delete")
    builder.adjust(2, 2)
    return builder.as_markup()
