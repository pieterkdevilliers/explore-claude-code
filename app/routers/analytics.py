from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_heroku_db
from app.models.heroku import HChatMessage, HChatSession
from app.schemas.analytics import (
    CountResponse,
    SentimentBreakdownResponse,
    SentimentCount,
)

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)],
)


def _cutoff() -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=30)


@router.get("/sessions/count", response_model=CountResponse)
async def global_session_count(db: AsyncSession = Depends(get_heroku_db)):
    """Total chat sessions started in the last 30 days."""
    result = await db.execute(
        select(func.count())
        .select_from(HChatSession)
        .where(HChatSession.start_time >= _cutoff())
    )
    return CountResponse(count=result.scalar_one())


@router.get("/messages/count", response_model=CountResponse)
async def global_message_count(db: AsyncSession = Depends(get_heroku_db)):
    """Total chat messages sent in the last 30 days."""
    result = await db.execute(
        select(func.count())
        .select_from(HChatMessage)
        .where(HChatMessage.timestamp >= _cutoff())
    )
    return CountResponse(count=result.scalar_one())


@router.get("/messages/by-sentiment", response_model=SentimentBreakdownResponse)
async def global_messages_by_sentiment(db: AsyncSession = Depends(get_heroku_db)):
    """Message count broken down by the session's initial_query_sentiment, last 30 days."""
    result = await db.execute(
        select(HChatSession.initial_query_sentiment, func.count(HChatMessage.message_id))
        .select_from(HChatMessage)
        .join(HChatSession, HChatMessage.chat_session_id == HChatSession.id)
        .where(HChatMessage.timestamp >= _cutoff())
        .group_by(HChatSession.initial_query_sentiment)
        .order_by(func.count(HChatMessage.message_id).desc())
    )
    rows = result.all()
    sentiments = [SentimentCount(sentiment=row[0], count=row[1]) for row in rows]
    return SentimentBreakdownResponse(sentiments=sentiments)
