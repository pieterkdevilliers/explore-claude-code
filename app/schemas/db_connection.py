from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class DbConnectionRequest(BaseModel):
    url: str


class DbConnectionTestResult(BaseModel):
    success: bool
    message: str
    server_version: Optional[str] = None


class DbConnectionStatus(BaseModel):
    configured: bool
    reachable: bool
    message: str
