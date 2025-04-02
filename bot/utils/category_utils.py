from sqlalchemy import select

from bot.database.database import get_session
from bot.models.category import Category


async def get_user_categories(user_id: int, category_type: str) -> list[str]:
    """
    Возвращает категории пользователя по типу (income/expense)
    """
    async with get_session() as session:
        result = await session.execute(
            select(Category.name)
            .where(
                Category.user_id == user_id,
                Category.type == category_type
            )
        )
        categories = [row[0] for row in result.all()]

        # Категории по умолчанию, если своих нет
        if not categories:
            return DEFAULT_CATEGORIES.get(category_type, [])
        return categories


DEFAULT_CATEGORIES = {
    "income": ["Зарплата", "Инвестиции", "Подарки"],
    "expense": ["Еда", "Транспорт", "Жильё"]
}
