from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from bot.database.database import Base
from datetime import datetime


class Category(Base):
    """
    Модель таблицы категории расходов
    """
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)  # 'income' или 'expense'
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="categories")
