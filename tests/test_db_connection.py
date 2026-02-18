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
        UserCreate(email="dbsuper@example.com", password="secret", is_superuser=True),
    )


@pytest.fixture
async def superuser_token(client: AsyncClient, superuser):
    login = await client.post(
        "/auth/login", json={"email": "dbsuper@example.com", "password": "secret"}
    )
    return login.json()["access_token"]


async def test_test_connection_invalid_url(client: AsyncClient, superuser_token):
    response = await client.post(
        "/db-connection/test",
        json={"url": "postgresql://invalid:5432/nodb"},
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Connection failed" in data["message"]


async def test_status_not_configured(client: AsyncClient, superuser_token, tmp_path, monkeypatch):
    # Point dotenv_values to a temp dir with no DATABASE_URL
    import app.routers.db_connection as db_conn_router

    monkeypatch.setattr(
        db_conn_router,
        "dotenv_values",
        lambda path: {},
    )
    response = await client.get(
        "/db-connection/status",
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["configured"] is False
    assert data["reachable"] is False
