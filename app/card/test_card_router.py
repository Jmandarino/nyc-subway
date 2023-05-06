import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def mock_session():
    from unittest import mock

    from mock_alchemy.mocking import UnifiedAlchemyMagicMock

    from app.train.schema import Station

    from .schema import Card

    return UnifiedAlchemyMagicMock(
        data=[
            (
                [
                    mock.call.query(Station),
                ],
                [Station(name="14th", cost=2)],
            ),
            (
                [
                    mock.call.query(Card),
                ],
                [Card(number=1234, balance=10)],
            ),
        ]
    )


def test_new_card(test_db):
    response = client.post("/card", json={"number": "1234", "balance": 10.0})
    assert response.status_code == 200
    assert response.json() == {"balance": 10.0}

    response = client.post("/card", json={"number": "1234", "balance": 10.0})
    assert response.status_code == 200
    assert response.json() == {"balance": 20.0}

    response = client.post("/card", json={"number": "12345", "balance": 10.0})
    assert response.status_code == 200
    assert response.json() == {"balance": 10.0}


def test_enter(test_db, mock_session):
    from .card_controller import TransactionType, create_transaction

    obj = create_transaction(mock_session, "14th", "1234", TransactionType.ENTER)
    assert obj == {"amount": 8}


def test_exit(test_db, mock_session):
    # An Exit keeps the same balance as before
    from .card_controller import TransactionType, create_transaction

    obj = create_transaction(mock_session, "14th", "1234", TransactionType.EXIT)
    assert obj == {"amount": 10}
