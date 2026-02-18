from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

import stripe as stripe_lib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_user, get_heroku_db
from app.models.heroku import HAccount, HChatMessage, HChatSession, HStripeSubscription
from app.schemas.account_read import AccountListResponse, AccountRead
from app.schemas.analytics import (
    CountResponse,
    SentimentBreakdownResponse,
    SentimentCount,
)
from app.schemas.stripe_read import (
    AccountStripeResponse,
    StripeCustomerRead,
    StripeInvoice,
    StripePaymentMethod,
    StripeSubscriptionRead,
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


# --- Stripe response helpers ---

def _parse_customer(res: object) -> Optional[StripeCustomerRead]:
    if isinstance(res, Exception):
        return None
    try:
        return StripeCustomerRead(
            id=res["id"],
            email=res.get("email"),
            name=res.get("name"),
            created=datetime.fromtimestamp(res["created"], tz=timezone.utc),
        )
    except Exception:
        return None


def _parse_payment_methods(res: object) -> list[StripePaymentMethod]:
    if isinstance(res, Exception):
        return []
    try:
        methods = []
        for pm in res.get("data", []):
            card = pm.get("card", {})
            if card:
                methods.append(StripePaymentMethod(
                    brand=card.get("brand", ""),
                    last4=card.get("last4", ""),
                    exp_month=card.get("exp_month", 0),
                    exp_year=card.get("exp_year", 0),
                ))
        return methods
    except Exception:
        return []


def _parse_invoices(res: object) -> list[StripeInvoice]:
    if isinstance(res, Exception):
        return []
    try:
        invoices = []
        for inv in res.get("data", []):
            invoices.append(StripeInvoice(
                id=inv["id"],
                number=inv.get("number"),
                amount_paid=inv.get("amount_paid", 0),
                currency=inv.get("currency", "usd"),
                status=inv.get("status"),
                created=datetime.fromtimestamp(inv["created"], tz=timezone.utc),
                invoice_pdf=inv.get("invoice_pdf"),
                hosted_invoice_url=inv.get("hosted_invoice_url"),
            ))
        return invoices
    except Exception:
        return []


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


# --- Stripe ---

@router.get("/{account_unique_id}/stripe", response_model=AccountStripeResponse)
async def account_stripe_data(
    account_unique_id: str,
    db: AsyncSession = Depends(get_heroku_db),
):
    """Subscription, payment method, and invoice data from Stripe for an account."""
    await _get_account_or_404(account_unique_id, db)

    # Look up subscription record stored in the Heroku DB
    result = await db.execute(
        select(HStripeSubscription).where(
            HStripeSubscription.account_unique_id == account_unique_id
        )
    )
    sub = result.scalar_one_or_none()

    if sub is None:
        return AccountStripeResponse(
            subscription=None, customer=None, payment_methods=[], invoices=[]
        )

    sub_read = StripeSubscriptionRead.model_validate(sub)

    # If no Stripe key, return DB data only (no live API calls)
    if not settings.stripe_secret_key:
        return AccountStripeResponse(
            subscription=sub_read, customer=None, payment_methods=[], invoices=[]
        )

    stripe_lib.api_key = settings.stripe_secret_key
    cid = sub.stripe_customer_id

    # Fetch customer, payment methods, and invoices concurrently
    customer_res, pm_res, invoices_res = await asyncio.gather(
        asyncio.to_thread(stripe_lib.Customer.retrieve, cid),
        asyncio.to_thread(stripe_lib.PaymentMethod.list, customer=cid, type="card"),
        asyncio.to_thread(stripe_lib.Invoice.list, customer=cid, limit=10),
        return_exceptions=True,
    )

    return AccountStripeResponse(
        subscription=sub_read,
        customer=_parse_customer(customer_res),
        payment_methods=_parse_payment_methods(pm_res),
        invoices=_parse_invoices(invoices_res),
    )
