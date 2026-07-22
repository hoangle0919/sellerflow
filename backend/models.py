import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

PLATFORMS = {"Shopee", "TikTok Shop", "Lazada"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class MerchantSubmission(BaseModel):
    shop_name: str = Field(min_length=1, max_length=120)
    platform: str          # "Shopee" | "TikTok Shop" | "Lazada"
    owner_name: str = Field(default="", max_length=120)
    phone: str = Field(default="", max_length=30)
    monthly_revenue: float = Field(gt=0, le=1e13)
    revenue_growth: float = Field(ge=-0.35, le=0.90)
    order_volume: int = Field(gt=0, le=10_000_000)
    avg_order_value: float = Field(gt=0, le=1e10)
    return_rate: float = Field(ge=0.0, le=0.40)
    rating: float = Field(ge=1.0, le=5.0)
    days_active: int = Field(gt=0, le=20_000)
    inventory_turnover: float = Field(ge=0.0, le=1000.0)
    late_ship_rate: float = Field(ge=0.0, le=0.40)
    previous_loans: int = Field(ge=0, le=1000)

    @field_validator("platform")
    @classmethod
    def platform_known(cls, v):
        if v not in PLATFORMS:
            raise ValueError(f"platform must be one of {sorted(PLATFORMS)}")
        return v


class WaitlistSignup(BaseModel):
    email: str = Field(max_length=254)
    company: Optional[str] = Field(default="", max_length=120)
    role: str = Field(max_length=30)   # "lender" | "seller" | "investor" | "other"

    @field_validator("email")
    @classmethod
    def email_valid(cls, v):
        v = v.strip().lower()
        if not EMAIL_RE.match(v):
            raise ValueError("invalid email address")
        return v


class LoginRequest(BaseModel):
    password: str = Field(max_length=200)


class KeyRequest(BaseModel):
    email: str = Field(max_length=254)
    company: Optional[str] = Field(default="", max_length=120)
    plan: str = Field(default="pilot", max_length=20)

    @field_validator("email")
    @classmethod
    def email_valid(cls, v):
        v = v.strip().lower()
        if not EMAIL_RE.match(v):
            raise ValueError("invalid email address")
        return v


class AssessmentResult(BaseModel):
    seller_id: str
    timestamp: str
    model_version: str
    decision: str          # "APPROVED" | "CONDITIONAL" | "REJECTED"
    pd_score: float
    pd_rf: float
    pd_lr: float
    credit_limit: float
    interest_rate: float
    risk_tier: str
    signals: dict
    reasoning: str


class OutcomeRecord(BaseModel):
    """Adjudicated repayment outcome — ground truth for the learning loop."""
    outcome: str = Field(pattern="^(repaid|late|defaulted)$")
    amount_remitted: Optional[float] = Field(default=None, ge=0, le=1e13)
    note: str = Field(default="", max_length=500)
