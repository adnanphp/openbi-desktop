"""Typed data models for OpenBI API responses."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HealthStatus:
    status: str
    version: str | None = None


@dataclass
class ExecutiveKPIs:
    revenue: float
    profit: float
    margin: float
    orders: int
    customers: int
    products: int
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class MonthlyRevenuePoint:
    month: str
    revenue: float


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
