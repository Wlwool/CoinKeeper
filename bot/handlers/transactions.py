from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class Transactions(StatesGroup):
    AMOUNT = State()
    CATEGORY = State()

@dp.message_handler(commands=["add_expense"])
async def cmd_add_expense(message: types.Message):
    await Transactions.AMOUNT.set()
    await message.answer("Введите сумму расхода: ")

@dp.message_handler(state=Transactions.AMOUNT)
async def get_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['amount'] = float(message.text)

    await Transactions.CATEGORY.set()
    await message.answer("Укажите категорию расхода: ")
