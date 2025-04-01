from aiogram import Dispatcher
from bot.handlers.basic_commands import register_handlers_basic_commands


def register_all_handlers(dp: Dispatcher):
    """Регистрирует все обработчики бота."""
    register_handlers_basic_commands(dp)

