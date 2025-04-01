import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from bot.config.config import Config
# from bot.models.user import User
# from bot.models.category import Category
# from bot.models.transactions import Transactions


logger = logging.getLogger(__name__)
config = Config()

Base = declarative_base() # базовый класс для создания моделей данных

# создаем асинхронный движок для взаимодействия с базой данных
engine = create_async_engine(config.DB_URL,
                             echo=True
                             )  # echo=True - выводит все запросы в консоль
# фабрика сессий для работы с базой данных
async_session = sessionmaker(engine,
                             class_=AsyncSession,
                             expire_on_commit=False
                             )


async def setup_db():
    """Инициализация и создание таблиц в базе данных."""
    try:
        async with engine.begin() as conn:
            logger.info("Создание таблиц в базе данных...")
            await conn.run_sync(Base.metadata.drop_all)   # УБРАТЬ ПОТОМ!!!
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Таблицы успешно созданы.")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")

    logger.info("Подключение к базе данных завершено.")

async def get_session() -> AsyncSession:
    """Генератор асинхронных сессий для работы с базой данных."""
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Ошибка при работе с сессией БД: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
