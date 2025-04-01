from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from bot.database.database import Base


class Category(Base):
    """
    Модель таблицы категории расходов
    """
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="category")

