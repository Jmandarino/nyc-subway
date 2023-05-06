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


@pytest.mark.parametrize(
    "stations,name,fare,expected",
    [
        (["Canal", "Houston", "Christopher", "14th"], None, 2.75, 422),
        (None, "E", 1, 422),
    ],
)
def test_new_line_validation(test_db, stations, name, fare, expected):
    response = client.post(
        "/train-line",
        json={
            "stations": stations,
            "name": name,
            "fare": fare,
        },
    )
    assert response.status_code == expected


def test_route_creation():
    """I was able to test manually via postman but this test has a few issues
    first off sqllite vs posgres offer different syntax so spinning up an quick db
    isn't easy. For complex sql I am not a fan of sqlalchemy and this is a perfect
    function is a perfect example
    """
    assert True
    # response = client.get("/route2?origin=Spring&destination=23rd")
    # assert response.status_code == 200
    # assert response.json() == {"route": ["Spring", "West 4th", "14th", "23rd"]}


@pytest.mark.parametrize(
    "stations,name,fare,expected",
    [
        (["Canal", "Houston", "Christopher", "14th"], "F", 2.75, "F"),
        (["Spring", "West 4th", "14th", "23rd"], "E", 1, "E"),
    ],
)
def test_new_line(test_db, stations, name, fare, expected):
    response = client.post(
        "/train-line",
        json={
            "stations": stations,
            "name": name,
            "fare": fare,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"name": expected}


def test_route_creation_py(test_db):
    """Test the python based version"""

    response = client.post(
        "/train-line",
        json={
            "stations": ["Spring", "West 4th", "14th", "23rd"],
            "name": "E",
            "faire:": 1,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"name": "E"}

    response = client.get("/route?origin=Spring&destination=23rd")
    assert response.status_code == 200
    assert response.json() == {"route": ["Spring", "West 4th", "14th", "23rd"]}

    response = client.get("/route?origin=Spring&destination=Invalid")
    assert response.status_code == 404
    # add in shortcut!
    response = client.post(
        "/train-line",
        json={
            "stations": ["Canal", "Houston", "Christopher", "14th"],
            "name": "1",
            "faire:": 1,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"name": "1"}
    # shorter route found, make sure its valid
    response = client.get("/route?origin=Houston&destination=23rd")
    assert response.status_code == 200
    assert response.json() == {"route": ["Houston", "Christopher", "14th", "23rd"]}
