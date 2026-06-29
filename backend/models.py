from pydantic import BaseModel
from typing import Optional


class SellerSubmission(BaseModel):
    shop_name: str
    platform: str          # "Shopee" | "TikTok Shop" | "Lazada"
    owner_name: str = ""
    phone: str = ""
    monthly_revenue: float
    revenue_growth: float  # -0.35 to 0.90
    order_volume: int
    avg_order_value: float
    return_rate: float     # 0.0 to 0.40
    rating: float          # 1.0 to 5.0
    days_active: int
    inventory_turnover: float
    late_ship_rate: float  # 0.0 to 0.40
    previous_loans: int


class WaitlistSignup(BaseModel):
    email: str
    company: Optional[str] = ""
    role: str              # "lender" | "seller" | "investor" | "other"


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
