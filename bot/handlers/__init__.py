from aiogram import Router
from .basic_commands import router as basic_router
from .transactions import router as transactions_router

main_router = Router()

main_router.include_router(basic_router)
main_router.include_router(transactions_router)


__all__ = ["main_router"]
