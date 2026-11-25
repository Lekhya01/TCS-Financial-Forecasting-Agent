
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ForecastRequest(BaseModel):
    task: str = Field(
        default="Analyze the last two quarters and forecast the upcoming quarter."
    )
    quarters: List[str] = Field(
        default_factory=lambda: ["Q1 FY27", "Q2 FY27"]
    )
    include_market_data: bool = False


class Metric(BaseModel):
    name: str
    latest_value: Optional[str] = None
    prior_value: Optional[str] = None
    growth_percentage: Optional[float] = None
    trend: str
    source: str


class ForecastResponse(BaseModel):
    company: str = "Tata Consultancy Services"
    ticker: str = "NSE:TCS"
    periods_analyzed: List[str]
    forecast_period: str

    outlook: Literal[
        "positive",
        "cautiously_positive",
        "neutral",
        "cautiously_negative",
        "negative"
    ]

    executive_summary: str
    financial_trends: List[Metric]
    management_outlook: List[str]
    opportunities: List[str]
    risks: List[str]
    assumptions: List[str]

    confidence: Literal["low", "medium", "high"]

    evidence_notes: List[str]

    disclaimer: str = (
        "Qualitative scenario analysis, not investment advice "
        "or a company-issued forecast."
    )
