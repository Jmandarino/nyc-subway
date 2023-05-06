from decimal import Decimal
from typing import List
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from app.database.db import get_db

from .train_controller import create_line, find_routes, find_routes_py

train_router = APIRouter()


class TrainLine(BaseModel):
    stations: Annotated[
        List[str],
        Body(
            title="List of stations of a line",
        ),
    ]
    name: Annotated[
        str,
        Body(
            title="Name of the Line",
        ),
    ]
    fare: Annotated[Decimal, Body(title="Cost of the line")] = Decimal(0)


class Route(BaseModel):
    origin: Annotated[
        str,
        Query(
            title="Name of the Origin station",
        ),
    ]
    destination: Annotated[
        str,
        Query(
            title="Name of the Destination station",
        ),
    ]


class RouteOut(BaseModel):
    route: List[str]

    @validator("route", pre=True)
    def split_string(cls, v):
        if isinstance(v, str):
            return v.split(",")
        return v


@train_router.post("/train-line")
async def create_train_line(trainline: TrainLine, db: Session = Depends(get_db)):
    """Creates a Train line with a given Name. Name must be unique however stations
    names can repeat

    Fare is optional but will default to 0 and can throw off downstream calculations
    """
    try:
        return {
            "name": create_line(db, trainline.stations, trainline.name, trainline.fare)
        }
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))


@train_router.get("/route2")
async def find_route(
    origin: str, destination: str, db: Session = Depends(get_db)
) -> RouteOut:
    """Not really being used -- recursive SQL version of route finding"""
    try:
        return RouteOut(route=find_routes(db, origin, destination))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@train_router.get("/route")
async def find_route(origin: str, destination: str, db: Session = Depends(get_db)):
    """Find the shortest route (based off number of stops) for a given route. Both
    Stops must be valid, this is implemented based of Dijkstra. No path found returns an exception
    """
    try:
        return RouteOut(route=find_routes_py(db, origin, destination))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
