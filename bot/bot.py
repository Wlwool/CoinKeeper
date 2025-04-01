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
        self.logger.info("Инициализация бота...")

    async def setup_db(self):
        """Настройка подключения к базе данных"""
        await setup_db()
        self.logger.info("Database connection successful.")


    def register_handlers(self):
        from bot.handlers import register_all_handlers
        register_all_handlers(self.dp)

    async def run(self):
        """Запуск бота"""
        await self.setup_db()
        self.register_handlers()
        self.logger.info("Запуск бота...")
        await self.dp.start_polling(self.bot)
