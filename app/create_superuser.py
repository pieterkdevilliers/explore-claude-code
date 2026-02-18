"""
Bootstrap script to create the first superuser.

Usage:
    uv run python -m app.create_superuser
"""
from __future__ import annotations

import asyncio

from app.database import LocalSessionFactory, init_local_db
from app.schemas.user import UserCreate
from app.services.user_service import create_user, get_user_by_email


async def main() -> None:
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    full_name = input("Full name (optional): ").strip() or None

    await init_local_db()

    async with LocalSessionFactory() as db:
        existing = await get_user_by_email(db, email)
        if existing:
            print(f"User '{email}' already exists (id={existing.id}).")
            return

        user = await create_user(
            db,
            UserCreate(
                email=email,
                password=password,
                full_name=full_name,
                is_superuser=True,
            ),
        )
        print(f"Superuser created: {user.email} (id={user.id})")


if __name__ == "__main__":
    asyncio.run(main())
