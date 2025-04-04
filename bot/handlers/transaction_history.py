from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select, desc
from datetime import datetime, timedelta, timezone
import logging
from bot.models.transactions import Transactions
from bot.database.database import get_session
from bot.keyboards.main_menu import main_menu_keyboard


router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("history"))
@router.message(F.text == "История транзакций")
async def show_history(message: Message):
    """
    Показывает историю транзакций пользователя за последние 30 дней
    """
    try:
        # получаем дату 30 дней назад
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

        async with get_session() as session:
            # запрос транзакций пользователя за последние 30 дней
            query = select(Transactions).where(
                Transactions.user_id == message.from_user.id,
                Transactions.date >= thirty_days_ago
            ).order_by(desc(Transactions.date))

            result = await session.execute(query)
            transactions = result.scalars().all()

            if not transactions:
                await message.answer("История транзакций пуста.", reply_markup=main_menu_keyboard()
                                     )
                return
            # формируем текст сообщения с историей транзакций
            history_text = "📊 История транзакций за последние 30 дней:\n\n"

            # группируем транзакции по дате
            transactions_by_date = {}
            for transaction in transactions:
                date_str = transaction.date.strftime("%d.%m.%Y")
                if date_str not in transactions_by_date:
                    transactions_by_date[date_str] = []
                transactions_by_date[date_str].append(transaction)

            # формируем текст сообщения с историей транзакций по дням
            for date_str, day_transactions in sorted(transactions_by_date.items(), reverse=True):
                history_text += f"📅 {date_str}:\n\n"

                for transaction in day_transactions:
                    emoji = "💰" if transaction.type == "income" else "💸"
                    sign = "+" if transaction.type == "income" else "-"
                    history_text += f"{emoji} {sign}{transaction.amount} руб. — {transaction.category}\n"
                history_text += "\n"

            # отправляет историю транзакций
            await message.answer(history_text, reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error(f"Ошибка при получении истории транзакций: {e}")
        await message.answer("Произошла ошибка при получении истории транзакций.",
                             reply_markup=main_menu_keyboard()
                             )
