from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class HerokuBase(DeclarativeBase):
    """Separate declarative base for the remote Heroku DB models.

    These are read-only reflections of the existing app's tables.
    create_all is never called against this base.
    """


class HAccount(HerokuBase):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_organisation: Mapped[str] = mapped_column(String)
    account_unique_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    k_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sources_returned: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    chunk_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_overlap: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    webhook_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    opt_in_webhook_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class HChatSession(HerokuBase):
    __tablename__ = "chatsession"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_unique_id: Mapped[str] = mapped_column(String, index=True)
    visitor_uuid: Mapped[str] = mapped_column(String, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    visitor_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    visitor_email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    initial_query_sentiment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    initial_query_sentiment_explanation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    conversation_sentiment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    conversation_sentiment_explanation: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class HChatMessage(HerokuBase):
    __tablename__ = "chatmessage"

    message_id: Mapped[str] = mapped_column(String, primary_key=True)
    chat_session_id: Mapped[int] = mapped_column(Integer, index=True)
    sender_type: Mapped[str] = mapped_column(String)
    message_text: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_files: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
