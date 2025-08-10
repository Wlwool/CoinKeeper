from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from bot.database.database import Base
from datetime import datetime


class Category(Base):
    """
    Модель таблицы категории расходов
    """
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_tg_id = Column(Integer, ForeignKey('users.user_tg_id', ondelete='CASCADE'),
                        nullable=False)
    name = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)  # 'income' или 'expense'
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="categories")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, type={self.type})>"
