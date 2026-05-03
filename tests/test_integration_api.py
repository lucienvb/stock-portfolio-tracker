from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Holding


@pytest.fixture
def client():
    test_client = TestClient(app)
    db = SessionLocal()
    try:
        db.query(Holding).delete()
        db.commit()
    finally:
        db.close()
    return test_client


def test_create_and_list_holdings(client):
    response = client.post(
        "/holdings",
        json={"symbol": "aapl", "shares": 5, "purchase_price": 100},
    )
    assert response.status_code == 201
    assert response.json()["symbol"] == "AAPL"

    list_response = client.get("/holdings")
    assert list_response.status_code == 200
    holdings = list_response.json()
    assert len(holdings) == 1
    assert holdings[0]["shares"] == 5


@patch("app.main.fetch_latest_price", return_value=120.0)
def test_portfolio_value_uses_latest_market_price(_, client):
    client.post(
        "/holdings",
        json={"symbol": "MSFT", "shares": 2, "purchase_price": 100},
    )

    response = client.get("/portfolio/value")
    assert response.status_code == 200
    payload = response.json()

    assert payload["total_market_value"] == 240.0
    assert payload["total_cost_basis"] == 200.0
    assert payload["total_gain_loss"] == 40.0
    assert payload["holdings"][0]["symbol"] == "MSFT"
