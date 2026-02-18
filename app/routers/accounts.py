from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_heroku_db
from app.models.heroku import HAccount, HChatMessage, HChatSession
from app.schemas.account_read import AccountListResponse, AccountRead
from app.schemas.analytics import (
    CountResponse,
    SentimentBreakdownResponse,
    SentimentCount,
)

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(get_current_user)],
)


def _cutoff() -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=30)


async def _get_account_or_404(account_unique_id: str, db: AsyncSession) -> HAccount:
    result = await db.execute(
        select(HAccount).where(HAccount.account_unique_id == account_unique_id)
    )
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


# --- Account listing ---

@router.get("/", response_model=AccountListResponse)
async def list_accounts(db: AsyncSession = Depends(get_heroku_db)):
    """List all user accounts from the Heroku DB."""
    result = await db.execute(select(HAccount).order_by(HAccount.account_organisation))
    accounts = result.scalars().all()
    return AccountListResponse(
        accounts=[AccountRead.model_validate(a) for a in accounts],
        total=len(accounts),
    )


# --- Per-account analytics ---

@router.get("/{account_unique_id}/sessions/count", response_model=CountResponse)
async def account_session_count(
    account_unique_id: str,
    db: AsyncSession = Depends(get_heroku_db),
):
    """Chat sessions for a specific account in the last 30 days."""
    await _get_account_or_404(account_unique_id, db)
    result = await db.execute(
        select(func.count())
        .select_from(HChatSession)
        .where(
            HChatSession.account_unique_id == account_unique_id,
            HChatSession.start_time >= _cutoff(),
        )
    )
    return CountResponse(count=result.scalar_one())


@router.get("/{account_unique_id}/messages/count", response_model=CountResponse)
async def account_message_count(
    account_unique_id: str,
    db: AsyncSession = Depends(get_heroku_db),
):
    """Chat messages for a specific account in the last 30 days."""
    await _get_account_or_404(account_unique_id, db)
    result = await db.execute(
        select(func.count())
        .select_from(HChatMessage)
        .join(HChatSession, HChatMessage.chat_session_id == HChatSession.id)
        .where(
            HChatSession.account_unique_id == account_unique_id,
            HChatMessage.timestamp >= _cutoff(),
        )
    )
    return CountResponse(count=result.scalar_one())


@router.get("/{account_unique_id}/messages/by-sentiment", response_model=SentimentBreakdownResponse)
async def account_messages_by_sentiment(
    account_unique_id: str,
    db: AsyncSession = Depends(get_heroku_db),
):
    """Message count by sentiment for a specific account, last 30 days."""
    await _get_account_or_404(account_unique_id, db)
    result = await db.execute(
        select(HChatSession.initial_query_sentiment, func.count(HChatMessage.message_id))
        .select_from(HChatMessage)
        .join(HChatSession, HChatMessage.chat_session_id == HChatSession.id)
        .where(
            HChatSession.account_unique_id == account_unique_id,
            HChatMessage.timestamp >= _cutoff(),
        )
        .group_by(HChatSession.initial_query_sentiment)
        .order_by(func.count(HChatMessage.message_id).desc())
    )
    rows = result.all()
    sentiments = [SentimentCount(sentiment=row[0], count=row[1]) for row in rows]
    return SentimentBreakdownResponse(sentiments=sentiments)
