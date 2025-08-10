from sqlalchemy import select

from bot.database.database import get_session
from bot.models.category import Category


async def get_user_categories(user_tg_id: int, category_type: str) -> list[str]:
    """
    Возвращает категории пользователя по типу (income/expense)

    Args:
        user_tg_id: Telegram ID пользователя
        category_type: Тип категории ('income' или 'expense')

    Returns:
        list[str]: Список названий категорий
    """
    async with get_session() as session:
        result = await session.execute(
            select(Category.name)
            .where(
                Category.user_tg_id == user_tg_id,
                Category.type == category_type
            )
        )
        categories = [row[0] for row in result.all()]

        # Категории по умолчанию, если своих нет
        if not categories:
            return DEFAULT_CATEGORIES.get(category_type, [])
        return categories


async def add_user_category(user_tg_id: int, name: str, category_type: str) -> bool:
    """
    Добавляет новую категорию для пользователя

    Args:
        user_tg_id: Telegram ID пользователя
        name: Название категории
        category_type: Тип категории ('income' или 'expense')

    Returns:
        bool: True если категория добавлена, False если уже существует
    """
    async with get_session() as session:
        # Проверяем, существует ли уже такая категория
        existing = await session.execute(
            select(Category)
            .where(
                Category.user_tg_id == user_tg_id,
                Category.name == name,
                Category.type == category_type
            )
        )

        if existing.scalar_one_or_none():
            return False

        # Создаем новую категорию
        category = Category(
            user_tg_id=user_tg_id,
            name=name,
            type=category_type
        )
        session.add(category)
        await session.commit()
        return True


DEFAULT_CATEGORIES = {
    "income": ["Зарплата", "Инвестиции", "Подарки", "Прочее"],
    "expense": ["Еда", "Транспорт", "Жильё", "Развлечения", "Медицина", "Прочее"]
}
