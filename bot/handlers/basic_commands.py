from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select
from datetime import datetime

from bot.keyboards.main_menu import main_menu_keyboard
from bot.database.database import get_session
from bot.models.user import User
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        # Регистрируем пользователя, если он еще не зарегистрирован
        async with get_session() as session:
            # Проверяем, существует ли пользователь
            user_query = await session.execute(
                select(User).where(User.user_tg_id == message.from_user.id)
            )
            user = user_query.scalar_one_or_none()

            if not user:
                # Создаем нового пользователя
                user = User(
                    user_tg_id=message.from_user.id,
                    username=message.from_user.username or "",
                    first_name=message.from_user.first_name or "",
                    last_name=message.from_user.last_name or ""
                )
                session.add(user)
                await session.commit()
                greeting = f"Добро пожаловать, {message.from_user.first_name}! Вы успешно зарегистрированы."
            else:
                greeting = f"С возвращением, {message.from_user.first_name}!"

        # Отправляем приветствие и информацию о боте
        await message.answer(
            f"{greeting}\n\n"
            "Я бот для учета финансов 💰.\n\n"
            "Доступные команды:\n"
            "/add_income - Добавить доход\n"
            "/add_expense - Добавить расход\n"
            "/history - Показать историю транзакций\n",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        logging.error(f"Ошибка при регистрации пользователя: {e}")
        await message.answer(
            "Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз.",
            reply_markup=main_menu_keyboard()
        )
