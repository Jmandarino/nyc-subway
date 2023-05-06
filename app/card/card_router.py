from decimal import Decimal
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from app.database.db import get_db

from .card_controller import TransactionType, create_card, create_transaction

card_router = APIRouter()


class Card(BaseModel):
    number: Annotated[
        str,
        Query(
            title="Unique Number of the card",
        ),
    ]
    balance: Annotated[Decimal, Query(title="Balance of the card", gt=0)] = 0

    @validator("balance")
    def gt_zero(cls, v):
        if v <= 0:
            raise ValueError("Balance must be a positive number")
        return v


# honestly it's silly we need this in fast api
class CardOut(BaseModel):
    balance: Annotated[Decimal, Query(title="Balance of the card remaining")]


class TransactionOut(BaseModel):
    amount: Annotated[
        Decimal, Query(title="Balance of the card remaining after Entrance/Exit")
    ]


@card_router.post("/card")
async def new_card(card: Card, db: Session = Depends(get_db)) -> CardOut:
    """Creates a new card, if the card exists add additional balance to it"""
    return CardOut(**create_card(db, **card.dict()))


@card_router.post("/station/{station}/enter")
def enter_station(
    station: Annotated[str, Path(description="Name of the station")],
    card: Card,
    db: Session = Depends(get_db),
) -> TransactionOut:
    """Tracks station entrance and card balance, will return a 404 exception if station doesn't exist
    Card balance station's cache the lowest price and will charge that upon entrance
    """
    try:
        return TransactionOut(
            **create_transaction(db, station, card.number, TransactionType.ENTER)
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@card_router.post("/station/{station}/exit")
def exit_station(
    station: Annotated[str, Path(description="Name of the station")],
    card: Card,
    db: Session = Depends(get_db),
) -> TransactionOut:
    """Tracks station Exit and returns current card balance, will return a 404 exception if station doesn't exist
    Card balance is looked up at the time of call and that balance is returned
    """
    try:
        return TransactionOut(
            **create_transaction(db, station, card.number, TransactionType.EXIT)
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
