from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from bot.database.database import Base


class User(Base):
    """
    Модель пользователя Telegram.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_tg_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))
    balance = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True)
    registered_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_tg_id}, username={self.username})>"
