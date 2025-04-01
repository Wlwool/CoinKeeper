from aiogram.types import Message
from bot.bot import TelegramBot
import logging
from aiogram import Router, types
from aiogram import Dispatcher, types
from aiogram.filters import Command
from sqlalchemy.future import select
# from bot.database.models import User
# from bot.database.database import async_session
from bot.keyboards.main_menu import main_menu_keyboard


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать! Я бот для учета финансов 💰.\n\n"
                         "Доступные команды:\n"
                         "/add_income - Добавить доход\n"
                         "/add_expense - Добавить расход\n"
                         "/history - Показать историю транзакций\n",
                         reply_markup=main_menu_keyboard()
                         )

