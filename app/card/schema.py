from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.types import DECIMAL, VARCHAR, Integer

from app.database.db import Base


class Card(Base):
    __tablename__ = "cards"

    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "balance": self.balance,
        }

    number = Column(VARCHAR(64), primary_key=True)
    balance = Column(DECIMAL)


class Transaction(Base):
    __tablename__ = "transactions"

    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "amount": self.balance_remaining,
        }

    id = Column("id", Integer, primary_key=True)
    card = Column(VARCHAR(64), ForeignKey("cards.number"), nullable=False)
    station = Column(Integer, ForeignKey("stations.id"), nullable=False)
    cost = Column("cost", DECIMAL, nullable=False)
    balance_remaining = Column("balance_remaining", DECIMAL, nullable=False)
    type = Column(
        "type",
        Enum("exit", "enter", name="transaction_type"),
        nullable=False,
    )
