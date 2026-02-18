from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate
from app.services.user_service import create_user


@pytest.fixture
async def superuser(db_session: AsyncSession):
    return await create_user(
        db_session,
        UserCreate(email="admin@example.com", password="secret", is_superuser=True),
    )


async def test_login_success(client: AsyncClient, superuser):
    response = await client.post(
        "/auth/login", json={"email": "admin@example.com", "password": "secret"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient, superuser):
    response = await client.post(
        "/auth/login", json={"email": "admin@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


async def test_me_returns_current_user(client: AsyncClient, superuser):
    login = await client.post(
        "/auth/login", json={"email": "admin@example.com", "password": "secret"}
    )
    token = login.json()["access_token"]
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"


async def test_me_unauthenticated(client: AsyncClient):
    response = await client.get("/auth/me")
    assert response.status_code == 401
