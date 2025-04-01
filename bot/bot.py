import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from bot.config.config import Config
from bot.utils.logger import setup_logger
from bot.database.database import setup_db


class TelegramBot:
    def __init__(self):
        setup_logger()
        self.logger = logging.getLogger(__name__)
        self.config = Config()

        # Redis в качестве хранилища состояний
        self.redis = Redis(host=self.config.REDIS_HOST,
                           port=self.config.REDIS_PORT,
                           db=self.config.REDIS_DB,
                           password=self.config.REDIS_PASSWORD,
                           decode_responses=True
                           )

        # инициализация бота и диспетчера
        self.bot = Bot(token=self.config.BOT_TOKEN)
        self.storage = RedisStorage(redis=self.redis)
        self.dp = Dispatcher(storage=self.storage)
        self.__register_routers()
        self.logger.info("Инициализация бота...")

    def __register_routers(self):
        from bot.handlers import main_router as handlers_router
        self.dp.include_router(handlers_router)

    async def setup_db(self):
        """Настройка подключения к базе данных"""
        from bot.models import User, Category, Transactions
        await setup_db()
        self.logger.info("База данных настроена!")


    async def run(self):
        """Запуск бота"""
        await self.setup_db()
        self.logger.info("Запуск бота...")
        await self.dp.start_polling(self.bot)
