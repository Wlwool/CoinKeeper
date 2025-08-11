from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy import select, desc, delete
import logging

from bot.models.transactions import Transactions
from bot.database.database import get_session
from bot.keyboards.main_menu import main_menu_keyboard
from bot.keyboards.delete_transactions import delete_transactions_keyboard, \
    confirm_delete_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("delete"))
@router.message(F.text == "🗑 Удалить транзакцию")
async def show_delete_menu(message: Message):
    """
    Показывает последние транзакции для удаления
    """
    try:
        async with get_session() as session:
            # Получаем последние 10 транзакций пользователя
            query = select(Transactions).where(
                Transactions.user_tg_id == message.from_user.id
            ).order_by(desc(Transactions.date)).limit(10)

            result = await session.execute(query)
            transactions = result.scalars().all()

            if not transactions:
                await message.answer(
                    "У вас нет транзакций для удаления.",
                    reply_markup=main_menu_keyboard()
                )
                return

            await message.answer(
                "🗑 Выберите транзакцию для удаления:\n\n"
                "Показаны последние 10 транзакций:",
                reply_markup=delete_transactions_keyboard(transactions)
            )

    except Exception as e:
        logger.error(f"Ошибка при получении транзакций для удаления: {e}")
        await message.answer(
            "Произошла ошибка при загрузке транзакций.",
            reply_markup=main_menu_keyboard()
        )


@router.callback_query(F.data.startswith("delete_transaction_"))
async def confirm_delete_transaction(callback: CallbackQuery):
    """
    Показывает подтверждение удаления транзакции
    """
    try:
        transaction_id = int(callback.data.split("_")[-1])

        async with get_session() as session:
            # Получаем информацию о транзакции
            query = select(Transactions).where(
                Transactions.id == transaction_id,
                Transactions.user_tg_id == callback.from_user.id
            )
            result = await session.execute(query)
            transaction = result.scalar_one_or_none()

            if not transaction:
                await callback.answer("Транзакция не найдена.", show_alert=True)
                return

            # Форматирование информации о транзакции
            emoji = "💰" if transaction.type == "income" else "💸"
            sign = "+" if transaction.type == "income" else "-"
            transaction_info = (
                f"{emoji} {sign}{transaction.amount} руб.\n"
                f"📁 Категория: {transaction.category}\n"
                f"📅 Дата: {transaction.date.strftime('%d.%m.%Y %H:%M')}"
            )

            await callback.message.edit_text(
                f"❓ Вы уверены, что хотите удалить эту транзакцию?\n\n"
                f"{transaction_info}",
                reply_markup=confirm_delete_keyboard(transaction_id)
            )

    except Exception as e:
        logger.error(f"Ошибка при подтверждении удаления: {e}")
        await callback.answer("Произошла ошибка.", show_alert=True)


@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_transaction(callback: CallbackQuery):
    """
    Удаляет транзакцию из базы данных
    """
    try:
        transaction_id = int(callback.data.split("_")[-1])

        async with get_session() as session:
            # Получение транзакции для логирования
            query = select(Transactions).where(
                Transactions.id == transaction_id,
                Transactions.user_tg_id == callback.from_user.id
            )
            result = await session.execute(query)
            transaction = result.scalar_one_or_none()

            if not transaction:
                await callback.answer("Транзакция не найдена.", show_alert=True)
                return

            # Удаляет транзакцию
            delete_query = delete(Transactions).where(
                Transactions.id == transaction_id,
                Transactions.user_tg_id == callback.from_user.id
            )
            await session.execute(delete_query)
            await session.commit()

            logger.info(
                f"Пользователь {callback.from_user.id} удалил транзакцию {transaction_id}")

            await callback.message.edit_text(
                f"✅ Транзакция успешно удалена!\n\n"
                f"💸 {transaction.amount} руб. - {transaction.category}",
                reply_markup=None
            )

            await callback.message.answer(
                "Главное меню:",
                reply_markup=main_menu_keyboard()
            )

    except Exception as e:
        logger.error(f"Ошибка при удалении транзакции: {e}")
        await callback.answer("Произошла ошибка при удалении.", show_alert=True)


@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    """
    Отменяет операцию удаления
    """
    await callback.message.edit_text("Удаление отменено.")
    await callback.message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard()
    )
