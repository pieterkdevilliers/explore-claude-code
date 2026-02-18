from __future__ import annotations

import re

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


# --- Local SQLite engine (admin users, always on) ---
local_engine: AsyncEngine = create_async_engine(
    settings.local_db_url,
    connect_args={"check_same_thread": False},
    echo=False,
)
LocalSessionFactory = async_sessionmaker(local_engine, expire_on_commit=False)


async def init_local_db() -> None:
    """Create all local SQLite tables if they don't exist (idempotent)."""
    async with local_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# --- On-demand Heroku Postgres engine factory ---
def make_heroku_engine(url: str) -> AsyncEngine:
    """Return an ephemeral asyncpg engine for a given Postgres URL."""
    normalized = re.sub(r"^postgres(ql)?://", "postgresql+asyncpg://", url)
    return create_async_engine(normalized, pool_pre_ping=True)


# --- Persistent Heroku engine (set at startup, reused across requests) ---
# Using a dict so init/dispose functions can mutate it without `global`.
_heroku: dict = {"engine": None, "session_factory": None}


def init_heroku_engine(url: str) -> None:
    """Create and store a persistent Heroku Postgres engine."""
    engine = make_heroku_engine(url)
    _heroku["engine"] = engine
    _heroku["session_factory"] = async_sessionmaker(engine, expire_on_commit=False)


async def dispose_heroku_engine() -> None:
    """Dispose the persistent Heroku engine on shutdown."""
    engine: AsyncEngine | None = _heroku.get("engine")
    if engine is not None:
        await engine.dispose()
        _heroku["engine"] = None
        _heroku["session_factory"] = None


def get_heroku_session_factory() -> async_sessionmaker | None:
    """Return the active Heroku session factory, or None if not configured."""
    return _heroku.get("session_factory")
