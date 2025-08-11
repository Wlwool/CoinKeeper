from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from bot.models.transactions import Transactions


def delete_transactions_keyboard(transactions: list[Transactions]) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для удаления транзакций
    
    Args:
        transactions: Список транзакций для отображения
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками удаления
    """
    builder = InlineKeyboardBuilder()
    
    for transaction in transactions:
        # Форматирует текст кнопки: эмодзи + сумма + категория
        emoji = "💰" if transaction.type == "income" else "💸"
        sign = "+" if transaction.type == "income" else "-"
        button_text = f"{emoji} {sign}{transaction.amount} - {transaction.category}"
        
        # Обрезаем текст если он слишком длинный
        if len(button_text) > 35:
            button_text = button_text[:32] + "..."
            
        builder.button(
            text=button_text,
            callback_data=f"delete_transaction_{transaction.id}"
        )

    builder.button(text="❌ Отменить", callback_data="cancel_delete")
    
    # По 1 кнопке в ряду для лучшей читаемости
    builder.adjust(1)
    
    return builder.as_markup()


def confirm_delete_keyboard(transaction_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения удаления транзакции
    
    Args:
        transaction_id: ID транзакции для удаления
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками подтверждения
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Да, удалить", callback_data=f"confirm_delete_{transaction_id}")
    builder.button(text="❌ Отменить", callback_data="cancel_delete")
    
    builder.adjust(2)
    
    return builder.as_markup()
