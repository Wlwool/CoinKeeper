from aiogram import Router, F
from aiogram.types import Message
import logging
from bot.keyboards.main_menu import main_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text, flags={"low_priority": True})
async def unknown_message(message: Message) -> None:
    """
    Обработка всего что не попадает в другие обработчики
    :param message:
    """
    logger.warning(f"Неизвестный ввод {message.from_user.id}: {message.text}")
    await message.answer(
        "Я не понимаю эту команду. Пожалуйста, используйте кнопки меню или команды.",
        reply_markup=main_menu_keyboard()
    )
