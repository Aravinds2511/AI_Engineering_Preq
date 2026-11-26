from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from ai_engineer_project.database import get_session
from ai_engineer_project.main import app
from ai_engineer_project.security import create_access_token


@pytest.fixture(name="client")
def client_fixture():
    """Provide a TestClient backed by an isolated in-memory SQLite database."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="registered_user")
def registered_user_fixture(client: TestClient) -> dict:
    """Register an isolated test user and return its credentials and ID."""
    payload = {"username": "testuser", "password": "strongpassword123"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    return {
        "id": data["id"],
        "username": payload["username"],
        "password": payload["password"],
    }


def test_valid_login(client: TestClient, registered_user: dict):
    response = client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
    assert data["token_type"] == "bearer"


def test_incorrect_password(client: TestClient, registered_user: dict):
    response = client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_missing_token(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_invalid_token(client: TestClient):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer this.is.not.a.valid.jwt"},
    )
    assert response.status_code == 401


def test_expired_token(client: TestClient, registered_user: dict):
    expired_token = create_access_token(
        data={"sub": str(registered_user["id"])},
        expires_delta=timedelta(seconds=-10),
    )
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


def test_valid_token(client: TestClient, registered_user: dict):
    login_resp = client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    me_resp = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["id"] == registered_user["id"]
    assert data["username"] == registered_user["username"]
    assert "hashed_password" not in data
