"""Typed data models for OpenBI API responses.

Field names match the actual OpenBI FastAPI responses.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HealthStatus:
    status: str
    version: str | None = None


@dataclass
class ExecutiveKPIs:
    total_revenue: float
    total_profit: float
    total_orders: int
    avg_order_value: float
    profit_margin_pct: float
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class MonthlyRevenuePoint:
    year: int
    month: int
    month_name: str
    revenue: float
    profit: float
    orders: int


@dataclass
class CategoryRevenue:
    category: str
    revenue: float


@dataclass
class CustomerSegment:
    cluster_label: str
    customers: int
    avg_recency_days: float
    avg_frequency: float
    avg_monetary: float
    total_monetary: float
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ForecastPoint:
    forecast_month: str          # ISO date string "2018-01-01"
    model_name: str
    yhat: float
    yhat_lower: float | None
    yhat_upper: float | None
    is_winner: bool


@dataclass
class ModelForecastSeries:
    """All forecast points for one model, plus derived helpers."""

    model_name: str
    is_winner: bool
    points: list[ForecastPoint]

    @property
    def total(self) -> float:
        return sum(p.yhat for p in self.points)

    @property
    def display_name(self) -> str:
        return {
            "ets": "ETS (Holt-Winters)",
            "xgboost": "XGBoost",
            "baseline_ma": "Baseline MA",
            "baseline": "Baseline",
        }.get(self.model_name, self.model_name.replace("_", " ").title())
