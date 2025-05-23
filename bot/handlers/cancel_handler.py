from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import logging

from bot.keyboards.main_menu import main_menu_keyboard
from bot.states.transactions import AddIncomeStates, AddExpenseStates

router = Router()
logger = logging.getLogger(__name__)


@router.message(
    F.text == "❌ Отменить",
    StateFilter(AddIncomeStates, AddExpenseStates),
    flags={"high_priority": True}  # Устанавливаем высокий приоритет
)
async def cancel_handler(message: Message, state: FSMContext):
    logger.info(f"Вызван обработчик отмены для пользователя {message.from_user.id}")
    current_state = await state.get_state()
    if current_state is None:
        logger.info("Нет активного состояния, отмена не требуется")
        return

    logger.info(f"Отмена состояния {current_state}")

    await state.clear()
    await message.answer(
        "Действие отменено!",
        reply_markup=main_menu_keyboard()
    )
    return True
