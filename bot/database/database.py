import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from bot.config.config import Config
from bot.database.base import Base
from contextlib import asynccontextmanager


logger = logging.getLogger(__name__)
config = Config()

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
    # Локальные импорты моделей для избежания циклических зависимостей
    from bot.models.user import User
    from bot.models.category import Category
    from bot.models.transactions import Transactions
    try:
        async with engine.begin() as conn:
            logger.info("Создание таблиц...")

            if 'sqlite' in config.DB_URL:
                await conn.execute(text("PRAGMA foreign_keys=ON"))

            # создание всех таблиц
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Таблицы созданы успешно")

    except Exception as e:
        logger.error(f"Критическая ошибка при создании таблиц: {e}")
        raise

@asynccontextmanager
async def get_session():
    """Асинхронный контекстный менеджер для работы с базой данных."""
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при работе с сессией БД: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()
