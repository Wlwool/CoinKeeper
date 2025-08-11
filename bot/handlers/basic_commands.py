from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select

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
                greeting = f"👋 Добро пожаловать, {message.from_user.first_name}!\n\nВы успешно зарегистрированы в боте учета финансов."
                logger.info(f"Новый пользователь зарегистрирован: {message.from_user.id}")
            else:
                greeting = f"👋 С возвращением, {message.from_user.first_name}!"

        # Отправляем приветствие и информацию о боте
        await message.answer(
            f"{greeting}\n\n"
            "💰 <b>Финансовый помощник</b> поможет вам:\n\n"
            "📈 Отслеживать доходы и расходы\n"
            "📊 Анализировать статистику\n"
            "⚙️ Управлять транзакциями\n"
            "📅 Просматривать историю\n\n"
            "<b>Доступные команды:</b>\n"
            "<code>/add_income</code> - Добавить доход\n"
            "<code>/add_expense</code> - Добавить расход\n"
            "<code>/history</code> - Показать историю\n"
            "<code>/history [дни]</code> - История за N дней\n"
            "<code>/delete</code> - Удалить транзакцию\n"
            "<code>/help</code> - Помощь\n\n"
            "Используйте кнопки меню для удобства! 👇",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя {message.from_user.id}: {e}")
        await message.answer(
            "❌ Произошла ошибка при запуске бота. Попробуйте еще раз.",
            reply_markup=main_menu_keyboard()
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
🤖 <b>Помощь по боту</b>

<b>Основные команды:</b>
<code>/start</code> - Запуск и регистрация
<code>/help</code> - Эта справка

<b>Управление транзакциями:</b>
<code>/add_income</code> - Добавить доход
<code>/add_expense</code> - Добавить расход  
<code>/delete</code> - Удалить транзакцию

<b>Просмотр данных:</b>
<code>/history</code> - Выбрать период истории
<code>/history 7</code> - История за 7 дней
<code>/history 30</code> - История за 30 дней
<code>/history [N]</code> - История за N дней

<b>Советы:</b>
• Используйте кнопки меню для удобства
• Для ввода суммы можно использовать точку или запятую
• История показывает последние операции с кратким итогом
• При удалении выбирайте из списка последних транзакций

<b>Поддержка:</b>
Если у вас возникли проблемы, перезапустите бота командой <code>/start</code>
"""

    await message.answer(
        help_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
