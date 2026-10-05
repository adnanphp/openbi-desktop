"""HTTP client for the OpenBI FastAPI backend."""

from __future__ import annotations

from typing import Any

import httpx

from .exceptions import APIError, ConnectionError_, ParseError
from .models import (
    CategoryRevenue,
    CustomerSegment,
    ExecutiveKPIs,
    ForecastPoint,
    HealthStatus,
    ModelForecastSeries,
    MonthlyRevenuePoint,
)


class OpenBIClient:
    """Synchronous client for the OpenBI API.

    All methods raise OpenBIError subclasses on failure. The GUI layer
    catches those and renders an error state.
    """

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # -- internals --------------------------------------------------------

    def _get(self, path: str, **params: Any) -> Any:
        url = f"{self.base_url}{path}"
        try:
            response = httpx.get(url, params=params or None, timeout=self.timeout)
        except httpx.RequestError as exc:
            raise ConnectionError_(f"Could not reach {url}: {exc}") from exc

        if response.status_code >= 400:
            raise APIError(response.status_code, response.text[:200])

        try:
            return response.json()
        except ValueError as exc:
            raise ParseError(f"Non-JSON response from {url}") from exc

    # -- endpoints --------------------------------------------------------

    def health(self) -> HealthStatus:
        data = self._get("/health")
        if isinstance(data, dict):
            return HealthStatus(
                status=str(data.get("status", "unknown")),
                version=data.get("version"),
            )
        raise ParseError("Unexpected /health response shape")

    def executive_kpis(self) -> ExecutiveKPIs:
        data = self._get("/kpis/executive")
        if not isinstance(data, dict):
            raise ParseError("Unexpected /kpis/executive response shape")
        return ExecutiveKPIs(
            total_revenue=float(data.get("total_revenue", 0)),
            total_profit=float(data.get("total_profit", 0)),
            total_orders=int(data.get("total_orders", 0)),
            avg_order_value=float(data.get("avg_order_value", 0)),
            profit_margin_pct=float(data.get("profit_margin_pct", 0)),
            raw=data,
        )

    def monthly_revenue(self) -> list[MonthlyRevenuePoint]:
        data = self._get("/kpis/monthly-revenue")
        if not isinstance(data, list):
            raise ParseError("Expected a list from /kpis/monthly-revenue")
        out: list[MonthlyRevenuePoint] = []
        for row in data:
            out.append(
                MonthlyRevenuePoint(
                    year=int(row.get("year", 0)),
                    month=int(row.get("month", 0)),
                    month_name=str(row.get("month_name", "")),
                    revenue=float(row.get("revenue", 0)),
                    profit=float(row.get("profit", 0)),
                    orders=int(row.get("orders", 0)),
                )
            )
        return out

    def revenue_by_category(self) -> list[CategoryRevenue]:
        data = self._get("/kpis/by-category")
        if not isinstance(data, list):
            raise ParseError("Expected a list from /kpis/by-category")
        return [
            CategoryRevenue(
                category=str(row.get("category", "")),
                revenue=float(row.get("revenue", 0)),
            )
            for row in data
        ]

    def customer_segments(self) -> list[CustomerSegment]:
        data = self._get("/customers/segments")
        if not isinstance(data, list):
            raise ParseError("Expected a list from /customers/segments")
        out: list[CustomerSegment] = []
        for row in data:
            out.append(
                CustomerSegment(
                    cluster_label=str(row.get("cluster_label", "")),
                    customers=int(row.get("customers", 0)),
                    avg_recency_days=float(row.get("avg_recency_days", 0)),
                    avg_frequency=float(row.get("avg_frequency", 0)),
                    avg_monetary=float(row.get("avg_monetary", 0)),
                    total_monetary=float(row.get("total_monetary", 0)),
                    raw=row,
                )
            )
        return out

    # -- forecasts --------------------------------------------------------

    def _parse_forecast_rows(self, data: Any) -> list[ForecastPoint]:
        if not isinstance(data, list):
            raise ParseError("Expected a list of forecast rows")
        out: list[ForecastPoint] = []
        for row in data:
            out.append(
                ForecastPoint(
                    forecast_month=str(row.get("forecast_month", "")),
                    model_name=str(row.get("model_name", "")),
                    yhat=float(row.get("yhat", 0)),
                    yhat_lower=(
                        float(row["yhat_lower"])
                        if row.get("yhat_lower") is not None
                        else None
                    ),
                    yhat_upper=(
                        float(row["yhat_upper"])
                        if row.get("yhat_upper") is not None
                        else None
                    ),
                    is_winner=bool(row.get("is_winner", False)),
                )
            )
        return out

    def latest_forecast(self) -> list[ForecastPoint]:
        """Forecast rows for the winning model only."""
        return self._parse_forecast_rows(self._get("/forecasts/latest"))

    def all_forecasts(self) -> list[ForecastPoint]:
        """Forecast rows for every candidate model."""
        return self._parse_forecast_rows(self._get("/forecasts/models"))

    def forecast_series_by_model(self) -> list[ModelForecastSeries]:
        """Group the all-models forecast into one entry per model."""
        rows = self.all_forecasts()
        groups: dict[str, list[ForecastPoint]] = {}
        winner: dict[str, bool] = {}
        for row in rows:
            groups.setdefault(row.model_name, []).append(row)
            winner[row.model_name] = winner.get(row.model_name, False) or row.is_winner

        result: list[ModelForecastSeries] = []
        for name, points in groups.items():
            points.sort(key=lambda p: p.forecast_month)
            result.append(
                ModelForecastSeries(
                    model_name=name,
                    is_winner=winner[name],
                    points=points,
                )
            )
        # Winner first, then by total descending.
        result.sort(key=lambda s: (not s.is_winner, -s.total))
        return result
