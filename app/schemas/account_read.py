from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_organisation: str
    account_unique_id: str
    relevance_score: Optional[float]
    k_value: Optional[int]
    sources_returned: Optional[int]
    temperature: Optional[float]
    chunk_size: Optional[int]
    chunk_overlap: Optional[int]
    webhook_url: Optional[str]
    opt_in_webhook_url: Optional[str]


class AccountListResponse(BaseModel):
    accounts: List[AccountRead]
    total: int
