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
        UserCreate(email="super@example.com", password="secret", is_superuser=True),
    )


@pytest.fixture
async def superuser_token(client: AsyncClient, superuser):
    login = await client.post(
        "/auth/login", json={"email": "super@example.com", "password": "secret"}
    )
    return login.json()["access_token"]


async def test_create_user(client: AsyncClient, superuser_token):
    response = await client.post(
        "/users/",
        json={"email": "new@example.com", "password": "pass123"},
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"


async def test_create_duplicate_user(client: AsyncClient, superuser_token):
    payload = {"email": "dup@example.com", "password": "pass123"}
    await client.post(
        "/users/", json=payload, headers={"Authorization": f"Bearer {superuser_token}"}
    )
    response = await client.post(
        "/users/", json=payload, headers={"Authorization": f"Bearer {superuser_token}"}
    )
    assert response.status_code == 400


async def test_list_users(client: AsyncClient, superuser_token):
    response = await client.get(
        "/users/", headers={"Authorization": f"Bearer {superuser_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_user_by_id(client: AsyncClient, superuser_token, superuser):
    response = await client.get(
        f"/users/{superuser.id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == superuser.id


async def test_update_user(client: AsyncClient, superuser_token, superuser):
    response = await client.patch(
        f"/users/{superuser.id}",
        json={"full_name": "Updated Name"},
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


async def test_delete_user(client: AsyncClient, superuser_token, db_session: AsyncSession):
    new_user = await create_user(
        db_session,
        UserCreate(email="todelete@example.com", password="pass"),
    )
    response = await client.delete(
        f"/users/{new_user.id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert response.status_code == 204
