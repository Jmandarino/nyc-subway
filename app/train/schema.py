from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import DECIMAL, Integer, String

from app.database.db import Base


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    # going to duplicate data here, its unlikely that a line is removed
    cost = Column(DECIMAL)


class TrainLine(Base):
    __tablename__ = "train_lines"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    cost = Column(DECIMAL)


class Connection(Base):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True)
    from_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    to_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    distance = Column(Integer, default=1)
    line = Column(Integer, ForeignKey("train_lines.id"), nullable=False)
