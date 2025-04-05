from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import StateFilter, Command
from datetime import datetime, timezone

from bot.states.transactions import AddIncomeStates, AddExpenseStates
from bot.keyboards.main_menu import main_menu_keyboard
from bot.keyboards.cancel import cancel_keyboard
from bot.keyboards.categories import categories_keyboard
from bot.models.transactions import Transactions
from bot.models.user import User
from bot.database.database import get_session
from bot.utils.category_utils import get_user_categories
import logging


router = Router()
logger = logging.getLogger(__name__)


# == ДОХОДЫ ==

@router.message(F.text == "Добавить доход", StateFilter(None))
@router.message(Command("add_income"), StateFilter(None))
async def start_add_income(message: Message, state: FSMContext):
    await message.answer(
        "Введите сумму дохода",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddIncomeStates.amount)


@router.message(AddIncomeStates.amount)
async def process_income_amount(message: Message, state: FSMContext):
    """Обработка введенной пользователем суммы дохода.

    Проверяет корректность введенной суммы (должна быть положительным числом),
    сохраняет ее в состоянии и переходит к выбору категории дохода.

    Args:
        message (Message): Сообщение пользователя с суммой дохода
        state (FSMContext): Контекст состояния пользователя
    """
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("Неверный формат суммы. Число должно быть больше 0.")
            return

        await state.update_data(amount=amount)  # Сохраняем сумму в состоянии

        categories = await get_user_categories(message.from_user.id, "income")
        await message.answer(
            "Выберите категорию:",
            reply_markup=categories_keyboard(categories)
        )
        await state.set_state(AddIncomeStates.category)
    except ValueError:
        await message.answer("Неверный формат суммы. Введите число.")


@router.message(AddIncomeStates.category)
async def process_income_category(message: Message, state: FSMContext):
    try:
        category = message.text
        data = await state.get_data()
        # Проверка категории
        valid_categories = await get_user_categories(message.from_user.id, "income")
        if category not in valid_categories:
            await message.answer("Выберите категорию из списка!")
            return

        # Сохранение
        async with get_session() as session:
            # Создаем транзакцию
            transaction = Transactions(
                user_id=message.from_user.id,
                amount=data['amount'],
                category=category,
                type="income",
                date=datetime.now(timezone.utc),
                price=data['amount']
            )
            session.add(transaction)
            await session.commit()
        # Показываем сообщение об успехе и возвращаем главное меню
        await message.answer(
            f"✅ Доход {data['amount']} руб. сохранён!",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")
        await message.answer("⚠️ Ошибка при сохранении дохода!", reply_markup=main_menu_keyboard())
    finally:
        await state.clear()


# ===================================РАСХОДЫ ===========================


@router.message(F.text == "Добавить расход", StateFilter(None))
@router.message(Command("add_expense"), StateFilter(None))
async def start_add_expense(message: Message, state: FSMContext):
    """Начало добавления расхода"""
    await message.answer(
        "Введите сумму расхода",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AddExpenseStates.amount)

@router.message(AddExpenseStates.amount)
async def process_expense_amount(message: Message, state: FSMContext):
    """Обработка суммы расхода"""
    # проверка на корректность суммы
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("Неверный формат суммы. Число должно быть больше 0.")
            return

        await state.update_data(amount=amount)  # сохраняем сумму в состоянии

        categories = await get_user_categories(message.from_user.id, "expense")
        await message.answer(
            "Выберите категорию:",
            reply_markup=categories_keyboard(categories)
        )
        await state.set_state(AddExpenseStates.category)
    except ValueError:
        await message.answer("Неверный формат суммы. Введите число.")

@router.message(AddExpenseStates.category)
async def process_expense_category(message: Message, state: FSMContext):
    """Обработка категории расхода и сохранение в БД"""
    try:
        category = message.text
        data = await state.get_data()

        # Проверка категории
        valid_categories = await get_user_categories(message.from_user.id, "expense")
        if category not in valid_categories:
            await message.answer("Выберите категорию из списка!")
            return

        # Сохранение
        async with get_session() as session:
            transaction = Transactions(
                user_id=message.from_user.id,
                amount=data['amount'],
                category=category,
                type="expense",
                date=datetime.now(timezone.utc),
                price=data['amount']
            )
            session.add(transaction)
            await session.commit()

        await message.answer(
            f"✅ Расход {data['amount']} руб. сохранён!",
            reply_markup=main_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")
        await message.answer("⚠️ Ошибка при сохранении расхода!", reply_markup=main_menu_keyboard())
    finally:
        await state.clear()
