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
    avg_monetary: float | None = None
    total_monetary: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ForecastPoint:
    month: str
    value: float


@dataclass
class ForecastModel:
    model: str
    mape: float
    rmse: float
    is_winner: bool = False
    raw: dict[str, Any] = field(default_factory=dict)
