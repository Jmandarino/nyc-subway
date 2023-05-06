from decimal import Decimal
from enum import Enum

from sqlalchemy.orm import Session

from app.train.schema import Station

from .schema import Card, Transaction


class TransactionType(Enum):
    ENTER = "enter"
    EXIT = "exit"


def hased_card(number: str) -> str:
    # TODO: We can get more secure but this is good for a POC
    # Better to use stripe or some 3rd party and store then anonymize token
    import hashlib

    return hashlib.sha256(number.encode()).hexdigest()


def create_card(session: Session, number: str, balance: Decimal):
    """Get or Create a card. if the card exists add balance to it"""
    number = hased_card(number)
    card = session.query(Card).filter(Card.number == number).first()

    if card:
        card.balance = card.balance + balance
    else:
        card = Card(number=number, balance=balance)
        session.add(card)
    session.commit()
    return card.serialize()


def create_transaction(
    session: Session,
    station_name: str,
    card_number: str,
    transaction_type: TransactionType,
):
    """Creates transactions for entering or exiting the system. Currently, we are
    using the transaction_type as a switch between the two types but if we expand
    on the difference it would be best to implement in a separate into two functions

    :param session: Db Connection
    :param station_name: station name to be looked up
    :param card_number: Card number to be looked up
    :param transaction_type: Enter / Exit
    :return: Dict["balance_remaining":Decimal]: Balance remaining
    """
    station = session.query(Station).filter(Station.name == station_name).first()
    if not station:
        raise ValueError(f"Station: {station_name} is not found")
    card = session.query(Card).filter(Card.number == hased_card(card_number)).first()
    if not card:
        raise ValueError(f"Card: {card_number} is not found")
    if transaction_type == TransactionType.ENTER:
        card.balance -= station.cost
    transaction = Transaction(
        card=card.number,
        station=station.id,
        cost=station.cost,
        balance_remaining=card.balance,
        type=transaction_type.value,
    )
    session.add(transaction)
    session.commit()

    return transaction.serialize()
