from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import StateFilter, Command
from datetime import datetime, timezone

from bot.states.transactions import AddIncomeStates, AddExpenseStates
from bot.keyboards.main_menu import main_menu_keyboard
from bot.keyboards.cancel import cancel_keyboard
from bot.keyboards.categories import categories_keyboard
from bot.models.transactions import Transactions
from bot.database.database import get_session
from bot.utils.category_utils import get_user_categories
import logging

router = Router()
logger = logging.getLogger(__name__)


# == ДОХОДЫ ==

@router.message(F.text == "💰 Добавить доход", StateFilter(None))
@router.message(Command("add_income"), StateFilter(None))
async def start_add_income(message: Message, state: FSMContext):
    await message.answer(
        "💰 Введите сумму дохода (в рублях):",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddIncomeStates.amount)


@router.message(AddIncomeStates.amount)
async def process_income_amount(message: Message, state: FSMContext):
    """Обработка введенной пользователем суммы дохода."""
    try:
        amount = float(
            message.text.replace(",", "."))  # Поддержка запятой как разделителя
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0. Попробуйте еще раз:")
            return

        await state.update_data(amount=amount)

        categories = await get_user_categories(message.from_user.id, "income")
        await message.answer(
            f"💰 Сумма: {amount} руб.\n\n"
            "📁 Выберите категорию дохода:",
            reply_markup=categories_keyboard(categories)
        )
        await state.set_state(AddIncomeStates.category)
    except ValueError:
        await message.answer(
            "❌ Неверный формат суммы. Введите число (например: 1000 или 1000.50):")


@router.message(AddIncomeStates.category)
async def process_income_category(message: Message, state: FSMContext):
    """Обработка категории дохода и сохранение в БД."""
    try:
        category = message.text
        data = await state.get_data()

        # Проверка категории
        valid_categories = await get_user_categories(message.from_user.id, "income")
        if category not in valid_categories:
            await message.answer("❌ Выберите категорию из списка или нажмите 'Отменить'!")
            return

        # Сохранение в БД
        async with get_session() as session:
            transaction = Transactions(
                user_tg_id=message.from_user.id,
                amount=data['amount'],
                category=category,
                type="income",
                date=datetime.now(timezone.utc)
            )
            session.add(transaction)
            await session.commit()

        logger.info(
            f"Пользователь {message.from_user.id} добавил доход: {data['amount']} руб. ({category})")

        await message.answer(
            f"✅ Доход успешно сохранён!\n\n"
            f"💰 +{data['amount']} руб.\n"
            f"📁 Категория: {category}",
            reply_markup=main_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Ошибка сохранения дохода: {e}")
        await message.answer(
            "❌ Произошла ошибка при сохранении дохода. Попробуйте еще раз.",
            reply_markup=main_menu_keyboard()
        )
    finally:
        await state.clear()


# == РАСХОДЫ ==

@router.message(F.text == "💸 Добавить расход", StateFilter(None))
@router.message(Command("add_expense"), StateFilter(None))
async def start_add_expense(message: Message, state: FSMContext):
    """Начало добавления расхода"""
    await message.answer(
        "💸 Введите сумму расхода (в рублях):",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddExpenseStates.amount)


@router.message(AddExpenseStates.amount)
async def process_expense_amount(message: Message, state: FSMContext):
    """Обработка суммы расхода"""
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0. Попробуйте еще раз:")
            return

        await state.update_data(amount=amount)

        categories = await get_user_categories(message.from_user.id, "expense")
        await message.answer(
            f"💸 Сумма: {amount} руб.\n\n"
            "📁 Выберите категорию расхода:",
            reply_markup=categories_keyboard(categories)
        )
        await state.set_state(AddExpenseStates.category)
    except ValueError:
        await message.answer(
            "❌ Неверный формат суммы. Введите число (например: 500 или 500.75):")


@router.message(AddExpenseStates.category)
async def process_expense_category(message: Message, state: FSMContext):
    """Обработка категории расхода и сохранение в БД"""
    try:
        category = message.text
        data = await state.get_data()

        # Проверка категории
        valid_categories = await get_user_categories(message.from_user.id, "expense")
        if category not in valid_categories:
            await message.answer("❌ Выберите категорию из списка или нажмите 'Отменить'!")
            return

        # Сохранение в БД
        async with get_session() as session:
            transaction = Transactions(
                user_tg_id=message.from_user.id,
                amount=data['amount'],
                category=category,
                type="expense",
                date=datetime.now(timezone.utc)
            )
            session.add(transaction)
            await session.commit()

        logger.info(
            f"Пользователь {message.from_user.id} добавил расход: {data['amount']} руб. ({category})")

        await message.answer(
            f"✅ Расход успешно сохранён!\n\n"
            f"💸 -{data['amount']} руб.\n"
            f"📁 Категория: {category}",
            reply_markup=main_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Ошибка сохранения расхода: {e}")
        await message.answer(
            "❌ Произошла ошибка при сохранении расхода. Попробуйте еще раз.",
            reply_markup=main_menu_keyboard()
        )
    finally:
        await state.clear()
