from aiogram import Router
from .cancel_handler import router as cancel_router
from .basic_commands import router as basic_router
from .transactions import router as transactions_router
from .transaction_history import router as history_router
from .unknown_handler import router as unknown_router

main_router = Router()

main_router.include_router(cancel_router)
main_router.include_router(basic_router)
main_router.include_router(transactions_router)
main_router.include_router(history_router)
main_router.include_router(unknown_router)

__all__ = ["main_router"]
