from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from bot.database.database import Base


class Transactions(Base):
    """
    Модель транзакций пользователей
    """

    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    price = Column(Float, nullable=False)

    user = relationship('Users', back_populates='transactions')
