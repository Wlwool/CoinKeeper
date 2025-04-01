from aiogram.types import Message
from bot.bot import TelegramBot
import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from sqlalchemy.future import select
# from bot.database.models import User
# from bot.database.database import async_session
# from bot.keyboards.reply import get_start_keyboard


async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для учета финансов. Используй /help для списка команд.")

async def cmd_help(message: Message):
    pass


def register_handlers_basic_commands(dp: Dispatcher) -> None:
    """  """
    dp.message.register(cmd_start, Command("start"))


