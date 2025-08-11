import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy import select, desc
from datetime import datetime, timedelta, timezone

from aiogram.fsm.context import FSMContext
from bot.states.transactions import AddIncomeStates, AddExpenseStates
from bot.models.transactions import Transactions
from bot.database.database import get_session
from bot.keyboards.main_menu import main_menu_keyboard, main_menu_inline_keyboard
from bot.keyboards.history import history_period_keyboard, history_stats_keyboard
from bot.keyboards.cancel import cancel_keyboard
from bot.keyboards.delete_transactions import delete_transactions_keyboard

router = Router()
logger = logging.getLogger(__name__)


def format_currency(amount: float) -> str:
    """Форматирует сумму с разделителем тысяч"""
    return f"{amount:,.2f}".replace(",", " ").replace(".00", "")


async def get_transactions_for_period(user_tg_id: int, days: int = None) -> list[Transactions]:
    """
    Получает транзакции пользователя за указанный период

    Args:
        user_tg_id: Telegram ID пользователя
        days: Количество дней (None = все время)

    Returns:
        list[Transactions]: Список транзакций
    """
    async with get_session() as session:
        query = select(Transactions).where(
            Transactions.user_tg_id == user_tg_id
        )

        if days is not None:
            date_from = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.where(Transactions.date >= date_from)

        query = query.order_by(desc(Transactions.date))

        result = await session.execute(query)
        return result.scalars().all()


def calculate_statistics(transactions: list[Transactions]) -> dict:
    """Вычисляет статистику по транзакциям"""
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    balance = total_income - total_expense

    # Группировка по категориям
    income_by_category = {}
    expense_by_category = {}

    for transaction in transactions:
        if transaction.type == "income":
            income_by_category[transaction.category] = income_by_category.get(
                transaction.category, 0) + transaction.amount
        else:
            expense_by_category[transaction.category] = expense_by_category.get(
                transaction.category, 0) + transaction.amount

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "income_by_category": income_by_category,
        "expense_by_category": expense_by_category,
        "transactions_count": len(transactions)
    }


def format_history_message(transactions: list[Transactions], period_text: str) -> str:
    """Форматирует сообщение с историей транзакций"""
    if not transactions:
        return f"📊 История транзакций {period_text}\n\nТранзакций не найдено."

    # Группируем транзакции по дням
    transactions_by_date = {}
    for transaction in transactions:
        date_str = transaction.date.strftime("%d.%m.%Y")
        if date_str not in transactions_by_date:
            transactions_by_date[date_str] = []
        transactions_by_date[date_str].append(transaction)

    message_parts = [f"📊 История транзакций {period_text}\n"]

    # Показываем только последние 10 дней для читаемости
    sorted_dates = sorted(transactions_by_date.keys(), reverse=True)
    displayed_dates = sorted_dates[:10]

    for date_str in displayed_dates:
        day_transactions = transactions_by_date[date_str]
        message_parts.append(f"\n📅 {date_str}:")

        for transaction in day_transactions[:5]:  # Максимум 5 транзакций за день
            emoji = "💰" if transaction.type == "income" else "💸"
            sign = "+" if transaction.type == "income" else "-"
            message_parts.append(
                f"{emoji} {sign}{format_currency(transaction.amount)} ₽ — {transaction.category}")

        if len(day_transactions) > 5:
            message_parts.append(f"   ... и ещё {len(day_transactions) - 5} транзакций")

    # Если показали не все дни
    if len(sorted_dates) > 10:
        message_parts.append(f"\n... и ещё {len(sorted_dates) - 10} дней")

    # Добавляем краткую статистику
    stats = calculate_statistics(transactions)
    message_parts.extend([
        "\n" + "=" * 30,
        f"📈 Доходы: +{format_currency(stats['total_income'])} ₽",
        f"📉 Расходы: -{format_currency(stats['total_expense'])} ₽",
        f"💰 Итого: {'+' if stats['balance'] >= 0 else ''}{format_currency(stats['balance'])} ₽",
        f"📊 Всего операций: {stats['transactions_count']}"
    ])

    return "\n".join(message_parts)


@router.message(Command("history"))
async def cmd_history(message: Message):
    """
    Обработчик команды /history с возможностью указания дней
    Примеры: /history, /history 7, /history 30
    """
    try:
        # Проверяем, указаны ли дни в команде
        command_parts = message.text.split()
        days = None

        if len(command_parts) > 1:
            try:
                days = int(command_parts[1])
                if days <= 0:
                    await message.answer("❌ Количество дней должно быть больше 0.")
                    return
            except ValueError:
                await message.answer(
                    "❌ Неверный формат команды.\n\n"
                    "Используйте:\n"
                    "/history - выбрать период\n"
                    "/history 7 - за 7 дней\n"
                    "/history 30 - за 30 дней"
                )
                return

        if days is None:
            # Показываем меню выбора периода
            await message.answer(
                "📊 Выберите период для просмотра истории транзакций:",
                reply_markup=history_period_keyboard()
            )
        else:
            # Показываем историю за указанное количество дней
            transactions = await get_transactions_for_period(message.from_user.id, days)
            period_text = f"за {days} дней" if days > 1 else "за 1 день"

            history_text = format_history_message(transactions, period_text)
            await message.answer(
                history_text,
                reply_markup=history_stats_keyboard(str(days))
            )

    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        await message.answer(
            "❌ Произошла ошибка при получении истории транзакций.",
            reply_markup=main_menu_keyboard()
        )


@router.message(F.text == "📊 История транзакций")
async def show_history_menu(message: Message):
    """Показывает меню выбора периода истории через кнопку"""
    await message.answer(
        "📊 Выберите период для просмотра истории транзакций:",
        reply_markup=history_period_keyboard()
    )


@router.callback_query(F.data.startswith("history_"))
async def process_history_callback(callback: CallbackQuery):
    """Обработка callback-запросов для истории"""
    try:
        action = callback.data.split("_", 1)[1]

        if action == "cancel":
            # Редактируем сообщение с inline-клавиатурой
            await callback.message.edit_text(
                "Главное меню:",
                reply_markup=main_menu_inline_keyboard()
            )
            await callback.answer()
            return

        if action == "choose_period":
            await callback.message.edit_text(
                "📊 Выберите период для просмотра истории транзакций:",
                reply_markup=history_period_keyboard()
            )
            await callback.answer()
            return

        if action == "main_menu":
            # Редактируем сообщение с inline-клавиатурой
            await callback.message.edit_text(
                "Главное меню:",
                reply_markup=main_menu_inline_keyboard()
            )
            await callback.answer()
            return

        # Определяем количество дней
        days_map = {
            "7": 7,
            "30": 30,
            "90": 90,
            "all": None
        }

        if action in days_map:
            days = days_map[action]
            transactions = await get_transactions_for_period(callback.from_user.id, days)

            if action == "all":
                period_text = "за все время"
            else:
                period_text = f"за {action} дней"

            history_text = format_history_message(transactions, period_text)

            await callback.message.edit_text(
                history_text,
                reply_markup=history_stats_keyboard(action)
            )
            await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при обработке callback истории: {e}")
        await callback.answer("❌ Произошла ошибка.", show_alert=True)


@router.callback_query(F.data.startswith("main_"))
async def process_main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка callback-запросов главного меню"""
    try:
        action = callback.data.split("_", 1)[1]

        if action == "history":
            await callback.message.edit_text(
                "📊 Выберите период для просмотра истории транзакций:",
                reply_markup=history_period_keyboard()
            )
        elif action == "add_income":
            # FSM для добавления дохода
            await callback.message.delete()
            await callback.bot.send_message(
                chat_id=callback.from_user.id,
                text="💰 Введите сумму дохода (в рублях):",
                reply_markup=cancel_keyboard()
            )
            await state.set_state(AddIncomeStates.amount)
        elif action == "add_expense":
            # FSM для добавления расхода
            await callback.message.delete()
            await callback.bot.send_message(
                chat_id=callback.from_user.id,
                text="💸 Введите сумму расхода (в рублях):",
                reply_markup=cancel_keyboard()
            )
            await state.set_state(AddExpenseStates.amount)
        elif action == "delete":

            async with get_session() as session:
                query = select(Transactions).where(
                    Transactions.user_tg_id == callback.from_user.id
                ).order_by(desc(Transactions.date)).limit(10)

                result = await session.execute(query)
                transactions = result.scalars().all()

                if not transactions:
                    await callback.message.edit_text(
                        "У вас нет транзакций для удаления.",
                        reply_markup=main_menu_inline_keyboard()
                    )
                    return

                await callback.message.edit_text(
                    "🗑 Выберите транзакцию для удаления:\n\n"
                    "Показаны последние 10 транзакций:",
                    reply_markup=delete_transactions_keyboard(transactions)
                )

        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при обработке callback главного меню: {e}")
        await callback.answer("❌ Произошла ошибка.", show_alert=True)


@router.callback_query(F.data.startswith("stats_"))
async def show_detailed_stats(callback: CallbackQuery):
    """Показывает детальную статистику за период"""
    try:
        period = callback.data.split("_", 1)[1]

        # Определяем количество дней
        days_map = {"7": 7, "30": 30, "90": 90, "all": None}
        days = days_map.get(period)

        transactions = await get_transactions_for_period(callback.from_user.id, days)
        stats = calculate_statistics(transactions)

        if not transactions:
            await callback.answer("Нет данных для статистики.", show_alert=True)
            return

        # Формируем сообщение со статистикой
        period_text = f"за {period} дней" if period != "all" else "за все время"

        stats_parts = [
            f"📊 Детальная статистика {period_text}\n",
            f"💰 Общий баланс: {'+' if stats['balance'] >= 0 else ''}{format_currency(stats['balance'])} ₽",
            f"📈 Доходы: +{format_currency(stats['total_income'])} ₽",
            f"📉 Расходы: -{format_currency(stats['total_expense'])} ₽",
            f"📊 Операций: {stats['transactions_count']}\n"
        ]

        # Топ категорий доходов
        if stats['income_by_category']:
            stats_parts.append("💰 Доходы по категориям:")
            sorted_income = sorted(stats['income_by_category'].items(),
                                   key=lambda x: x[1], reverse=True)
            for category, amount in sorted_income[:5]:
                stats_parts.append(f"  • {category}: +{format_currency(amount)} ₽")
            if len(sorted_income) > 5:
                stats_parts.append(f"  ... и ещё {len(sorted_income) - 5} категорий")
            stats_parts.append("")

        # Топ категорий расходов
        if stats['expense_by_category']:
            stats_parts.append("💸 Расходы по категориям:")
            sorted_expenses = sorted(stats['expense_by_category'].items(),
                                     key=lambda x: x[1], reverse=True)
            for category, amount in sorted_expenses[:5]:
                stats_parts.append(f"  • {category}: -{format_currency(amount)} ₽")
            if len(sorted_expenses) > 5:
                stats_parts.append(f"  ... и ещё {len(sorted_expenses) - 5} категорий")

        await callback.message.edit_text(
            "\n".join(stats_parts),
            reply_markup=history_stats_keyboard(period)
        )

    except Exception as e:
        logger.error(f"Ошибка при показе статистики: {e}")
        await callback.answer("❌ Произошла ошибка.", show_alert=True)