import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Holding


class TestPortfolioAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        db = SessionLocal()
        try:
            db.query(Holding).delete()
            db.commit()
        finally:
            db.close()

    def test_create_and_list_holdings(self):
        response = self.client.post(
            "/holdings",
            json={"symbol": "aapl", "shares": 5, "purchase_price": 100},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["symbol"], "AAPL")

        list_response = self.client.get("/holdings")
        self.assertEqual(list_response.status_code, 200)
        holdings = list_response.json()
        self.assertEqual(len(holdings), 1)
        self.assertEqual(holdings[0]["shares"], 5)

    @patch("app.main.fetch_latest_price", return_value=120.0)
    def test_portfolio_value_uses_latest_market_price(self, _):
        self.client.post(
            "/holdings",
            json={"symbol": "MSFT", "shares": 2, "purchase_price": 100},
        )

        response = self.client.get("/portfolio/value")
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["total_market_value"], 240.0)
        self.assertEqual(payload["total_cost_basis"], 200.0)
        self.assertEqual(payload["total_gain_loss"], 40.0)
        self.assertEqual(payload["holdings"][0]["symbol"], "MSFT")
