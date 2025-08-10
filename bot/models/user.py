from bot.database.base import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    """
    Модель пользователя Telegram.
    """
    __tablename__ = 'users'

    user_tg_id = Column(Integer, primary_key=True)
    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))
    balance = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True)
    registered_at = Column(DateTime, server_default=func.now())

    categories = relationship("Category", back_populates="user",
                              cascade="all, delete-orphan")
    transactions = relationship("Transactions", back_populates="user",
                                cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_tg_id={self.user_tg_id}, username={self.username})>"
