from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class CountResponse(BaseModel):
    count: int
    period_days: int = 30


class SentimentCount(BaseModel):
    sentiment: Optional[str]  # None = unclassified sessions
    count: int


class SentimentBreakdownResponse(BaseModel):
    sentiments: List[SentimentCount]
    period_days: int = 30
