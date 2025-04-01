from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import StateFilter, Command
from datetime import datetime

from bot.states.transactions import AddIncomeStates, AddExpenseStates
from bot.keyboards.cancel import cancel_keyboard
from bot.keyboards.categories import categories_keyboard
from bot.models.transactions import Transactions
from bot.database.database import get_session


router = Router()

# == ДОХОДЫ
@router.message(F.text == "Добавить доход", StateFilter(None))
@router.message(Command("add_income"), StateFilter(None))
async def start_add_income(message: Message, state: FSMContext):
    await message.answer(
        "Введите сумму дохода",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AddIncomeStates.amount)


@router.message(AddIncomeStates.amount)
async def process_income_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError

        await state.update_data(amount=amount)
        await message.answer("Укажите категорию: ",
                             reply_markup=categories_keyboard(["Зарплата", "Инвестиции", "Подарки", "Другое"])
                             )

        await state.set_state(AddIncomeStates.category)
    except ValueError:
        await message.answer(
            "Неверный формат суммы. Пожалуйста, введите сумму снова. Число должно быть больше 0"
        )


@router.message(AddIncomeStates.category)
async def process_income_category(message: Message, state: FSMContext):
    category = message.text
    data = await state.get_data()

    # Сохранение дохода в базе данных
    async with get_session() as session:
        transaction = Transactions(
            amount=data["amount"],
            type="income",
            category=category,
            user_id=message.from_user.id,
            date=datetime.now(),
            price=data["amount"]
        )
    session.add(transaction)
    await session.commit()

    await message.answer(
        f"✅ Доход {data['amount']} руб. по категории '{category}' сохранён!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

# == РАСХОДЫ

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
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError

        await state.update_data(amount=amount)

        expense_categories = ["Еда", "Транспорт", "Жильё", "Развлечения"]

        await message.answer(
            "Укажите категорию расхода:",
            reply_markup=categories_keyboard(expense_categories)
        )
        await state.set_state(AddExpenseStates.category)
    except ValueError:
        await message.answer("Неверный формат суммы. Пожалуйста, введите сумму снова. Число должно быть больше 0")

@router.message(AddExpenseStates.category)
async def process_expense_category(message: Message, state: FSMContext):
    """Обработка категории расхода и сохранение в БД"""
    category = message.text
    data = await state.get_data()

    # Валидация категории
    if len(category) > 50:
        await message.answer("Название категории не должно превышать 50 символов!")
        return

    async with get_session() as session:
        transaction = Transactions(
            amount=data["amount"],
            type="expense",
            category=category,
            user_id=message.from_user.id,
            date=datetime.now(),
            price=data["amount"]
        )
        session.add(transaction)
        await session.commit()

    await message.answer(
        f"✅ Расход {data['amount']} руб. по категории '{category}' сохранён!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


# == ОТМЕНА
@router.message(F.text == "Отменить")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Действие отменено!",
        reply_markup=ReplyKeyboardRemove()
    )

