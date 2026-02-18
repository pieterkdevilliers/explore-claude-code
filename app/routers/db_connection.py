from __future__ import annotations

from dotenv import dotenv_values
from fastapi import APIRouter, Depends, HTTPException

from app.database import dispose_heroku_engine, init_heroku_engine
from app.dependencies import require_superuser
from app.schemas.db_connection import (
    DbConnectionRequest,
    DbConnectionStatus,
    DbConnectionTestResult,
)
from app.services import db_connection_service

router = APIRouter(
    prefix="/db-connection",
    tags=["db-connection"],
    dependencies=[Depends(require_superuser)],
)


@router.post("/test", response_model=DbConnectionTestResult)
async def test_db_connection(body: DbConnectionRequest):
    """Test a Postgres connection URL without saving it."""
    success, message, version = await db_connection_service.test_connection(body.url)
    return DbConnectionTestResult(success=success, message=message, server_version=version)


@router.post("/save", response_model=DbConnectionTestResult)
async def save_db_connection(body: DbConnectionRequest):
    """Test a Postgres connection URL and, if successful, persist it to .env."""
    success, message, version = await db_connection_service.test_connection(body.url)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    await db_connection_service.save_connection_url(body.url)
    # Hot-reload the persistent engine so analytics endpoints work immediately
    await dispose_heroku_engine()
    init_heroku_engine(body.url)
    return DbConnectionTestResult(
        success=True,
        message="Connection verified, saved to .env, and active.",
        server_version=version,
    )


@router.get("/status", response_model=DbConnectionStatus)
async def db_connection_status():
    """Check whether a DATABASE_URL is configured and the DB is currently reachable."""
    env_values = dotenv_values(".env")
    url = env_values.get("DATABASE_URL")

    if not url:
        return DbConnectionStatus(
            configured=False,
            reachable=False,
            message="DATABASE_URL is not set in .env",
        )

    success, message, _ = await db_connection_service.test_connection(url)
    return DbConnectionStatus(configured=True, reachable=success, message=message)
