from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import dispose_heroku_engine, init_heroku_engine, init_local_db
from app.routers import accounts, analytics, auth, db_connection, users


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: ensure local SQLite tables exist
    await init_local_db()
    # If DATABASE_URL is already configured, connect to Heroku DB immediately
    if settings.database_url:
        init_heroku_engine(settings.database_url)
    yield
    # Shutdown: release Heroku connection pool
    await dispose_heroku_engine()


app = FastAPI(
    title="Management Overview API",
    version="0.1.0",
    description="Backend for the management/overview interface.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(db_connection.router)
app.include_router(analytics.router)
app.include_router(accounts.router)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}
