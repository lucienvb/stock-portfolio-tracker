import unittest
from unittest.mock import Mock, patch

import requests

from app.services import fetch_latest_price


class TestFetchLatestPrice(unittest.TestCase):
    @patch("app.services.requests.get")
    def test_fetch_latest_price_parses_close_column(self, mock_get):
        mock_response = Mock()
        mock_response.text = "Symbol,Date,Time,Open,High,Low,Close,Volume\nAAPL.US,2026-01-01,22:00:00,100,101,99,123.45,1000\n"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        price = fetch_latest_price("AAPL")

        self.assertEqual(price, 123.45)

    @patch("app.services.requests.get")
    def test_fetch_latest_price_returns_none_on_request_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException("network issue")

        price = fetch_latest_price("AAPL")

        self.assertIsNone(price)
