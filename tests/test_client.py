"""Tests for the OpenBI API client using httpx's mock transport."""

import httpx
import pytest

from openbi_desktop.api.client import OpenBIClient
from openbi_desktop.api.exceptions import APIError, ConnectionError_


def make_client(handler) -> OpenBIClient:
    """Build a client whose HTTP calls are intercepted by `handler`."""
    client = OpenBIClient("http://test.invalid")

    # Monkey-patch httpx.get to route through a MockTransport.
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
                "revenue": 2297200.86,
                "profit": 286397.02,
                "margin": 12.47,
                "orders": 5009,
                "customers": 793,
                "products": 1862,
            },
        )

    client = make_client(handler)
    kpis = client.executive_kpis()
    assert kpis.revenue == pytest.approx(2297200.86)
    assert kpis.orders == 5009
