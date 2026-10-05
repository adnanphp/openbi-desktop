"""Tests for the OpenBI API client using httpx's mock transport."""

import httpx
import pytest

from openbi_desktop.api.client import OpenBIClient
from openbi_desktop.api.exceptions import APIError, ConnectionError_


def make_client(handler) -> OpenBIClient:
    """Build a client whose HTTP calls are intercepted by `handler`."""
    client = OpenBIClient("http://test.invalid")
    transport = httpx.MockTransport(handler)

    def fake_get(url, params=None, timeout=None):
        with httpx.Client(transport=transport) as c:
            return c.get(url, params=params, timeout=timeout)

    client._get.__globals__["httpx"].get = fake_get  # type: ignore[attr-defined]
    return client


def test_health_ok():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "ok", "version": "1.0"})

    client = make_client(handler)
    result = client.health()
    assert result.status == "ok"
    assert result.version == "1.0"


def test_http_error_raises_api_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    client = make_client(handler)
    with pytest.raises(APIError):
        client.health()


def test_connection_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route")

    client = make_client(handler)
    with pytest.raises(ConnectionError_):
        client.health()


def test_executive_kpis():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "total_revenue": 2297200.8603,
                "total_profit": 286397.0217,
                "total_orders": 5009,
                "avg_order_value": 458.6146656618088,
                "profit_margin_pct": 12.47,
            },
        )

    client = make_client(handler)
    kpis = client.executive_kpis()
    assert kpis.total_revenue == pytest.approx(2297200.8603)
    assert kpis.total_orders == 5009
    assert kpis.profit_margin_pct == pytest.approx(12.47)


def test_monthly_revenue():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "year": 2014,
                    "month": 1,
                    "month_name": "Jan",
                    "revenue": 14236.895,
                    "profit": 2450.1907,
                    "orders": 32,
                },
                {
                    "year": 2014,
                    "month": 2,
                    "month_name": "Feb",
                    "revenue": 4519.892,
                    "profit": 862.3084,
                    "orders": 28,
                },
            ],
        )

    client = make_client(handler)
    points = client.monthly_revenue()
    assert len(points) == 2
    assert points[0].year == 2014
    assert points[0].month_name == "Jan"
    assert points[0].revenue == pytest.approx(14236.895)

def test_customer_segments():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "cluster_label": "Champions",
                    "customers": 106,
                    "avg_recency_days": 24.5,
                    "avg_frequency": 9.31,
                    "avg_monetary": 5287.72,
                    "total_monetary": 560498.83,
                },
                {
                    "cluster_label": "At Risk",
                    "customers": 102,
                    "avg_recency_days": 220.4,
                    "avg_frequency": 7.75,
                    "avg_monetary": 4399.61,
                    "total_monetary": 448760.05,
                },
            ],
        )

    client = make_client(handler)
    segments = client.customer_segments()
    assert len(segments) == 2
    assert segments[0].cluster_label == "Champions"
    assert segments[0].customers == 106
    assert segments[0].avg_monetary == pytest.approx(5287.72)
    assert segments[1].total_monetary == pytest.approx(448760.05)
