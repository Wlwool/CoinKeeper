from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from bot.database.database import Base
from datetime import datetime


class Transactions(Base):
    """
    Модель транзакций пользователей
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_tg_id = Column(Integer, ForeignKey('users.user_tg_id', ondelete='CASCADE'),
                        nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    type = Column(String(10), nullable=False)  # 'income' или 'expense'
    description = Column(String(255),
                         nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.now)

    user = relationship('User', back_populates='transactions')

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, category={self.category}, type={self.type})>"
