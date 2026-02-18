from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class StripeSubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stripe_subscription_id: str
    stripe_customer_id: str
    status: Optional[str]
    current_period_end: Optional[datetime]
    type: Optional[str]
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    subscription_start: Optional[datetime]
    stripe_account_url: Optional[str]
    related_product_title: Optional[str]


class StripeCustomerRead(BaseModel):
    id: str
    email: Optional[str]
    name: Optional[str]
    created: datetime


class StripePaymentMethod(BaseModel):
    brand: str
    last4: str
    exp_month: int
    exp_year: int


class StripeInvoice(BaseModel):
    id: str
    number: Optional[str]
    amount_paid: int  # in cents
    currency: str
    status: Optional[str]
    created: datetime
    invoice_pdf: Optional[str]
    hosted_invoice_url: Optional[str]


class AccountStripeResponse(BaseModel):
    subscription: Optional[StripeSubscriptionRead]
    customer: Optional[StripeCustomerRead]
    payment_methods: List[StripePaymentMethod]
    invoices: List[StripeInvoice]
