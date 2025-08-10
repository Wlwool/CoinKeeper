import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage
from redis.asyncio import Redis
from bot.config.config import Config
from bot.utils.logger import setup_logger
from bot.database.database import setup_db


class TelegramBot:
    def __init__(self):
        setup_logger()
        self.logger = logging.getLogger(__name__)
        self.config = Config()

        # Инициализация бота
        self.bot = Bot(token=self.config.BOT_TOKEN)

        # Выбираем хранилище состояний
        if self.config.USE_REDIS:
            try:
                self.logger.info("Инициализация Redis...")
                self.redis = Redis(
                    host=self.config.REDIS_HOST,
                    port=self.config.REDIS_PORT,
                    db=self.config.REDIS_DB,
                    password=self.config.REDIS_PASSWORD if self.config.REDIS_PASSWORD else None,
                    decode_responses=True
                )
                self.storage = RedisStorage(redis=self.redis)
                self.logger.info("Redis хранилище подключено")
            except Exception as e:
                self.logger.warning(f"Ошибка подключения к Redis: {e}")
                self.logger.info("Переключение на MemoryStorage...")
                self.storage = MemoryStorage()
        else:
            self.logger.info("Использование MemoryStorage...")
            self.storage = MemoryStorage()

        # Инициализация диспетчера
        self.dp = Dispatcher(storage=self.storage)
        self.__register_routers()
        self.logger.info("Бот инициализирован успешно!")

    def __register_routers(self):
        from bot.handlers import main_router as handlers_router
        self.dp.include_router(handlers_router)

    async def setup_db(self):
        """Настройка подключения к базе данных"""
        try:
            await setup_db()
            self.logger.info("База данных настроена!")
        except Exception as e:
            self.logger.error(f"Ошибка настройки БД: {e}")
            raise

    async def run(self):
        """Запуск бота"""
        try:
            await self.setup_db()
            self.logger.info("Запуск polling...")
            await self.dp.start_polling(self.bot)
        except KeyboardInterrupt:
            self.logger.info("Бот остановлен")
        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
            raise
        finally:
            await self.bot.session.close()
            if hasattr(self, 'redis'):
                await self.redis.close()