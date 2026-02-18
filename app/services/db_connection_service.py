from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import text

from app.database import make_heroku_engine


async def test_connection(url: str) -> Tuple[bool, str, Optional[str]]:
    """
    Test a Postgres connection URL. Returns (success, message, server_version).
    The engine is disposed immediately after the test.
    """
    engine = None
    try:
        engine = make_heroku_engine(url)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version: Optional[str] = result.scalar()
        return True, "Connection successful", version
    except Exception as exc:
        return False, f"Connection failed: {exc}", None
    finally:
        if engine is not None:
            await engine.dispose()


async def save_connection_url(url: str, env_path: str = ".env") -> None:
    """
    Write or update DATABASE_URL in the .env file.
    Reads existing content, replaces the key if present, appends if not.
    """
    try:
        with open(env_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    key = "DATABASE_URL"
    new_line = f"{key}={url}\n"
    found = False
    new_lines = []

    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(new_line)
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(new_line)

    with open(env_path, "w") as f:
        f.writelines(new_lines)
