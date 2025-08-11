from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def history_period_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора периода истории транзакций
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками выбора периода
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📅 За 7 дней", callback_data="history_7")
    builder.button(text="📅 За 30 дней", callback_data="history_30")
    builder.button(text="📅 За 90 дней", callback_data="history_90")
    builder.button(text="📅 Все время", callback_data="history_all")
    builder.button(text="❌ Отменить", callback_data="history_cancel")
    builder.adjust(2, 2, 1)

    return builder.as_markup()


def history_stats_keyboard(days: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с дополнительными опциями после показа истории
    
    Args:
        days: Период для которого показана история
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с дополнительными опциями
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📊 Статистика", callback_data=f"stats_{days}")
    builder.button(text="🔄 Другой период", callback_data="history_choose_period")
    builder.button(text="🏠 В главное меню", callback_data="history_main_menu")
    builder.adjust(1)
    
    return builder.as_markup()