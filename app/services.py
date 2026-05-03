from io import StringIO
from typing import Optional

import pandas as pd
import requests


def fetch_latest_price(symbol: str) -> Optional[float]:
    ticker = symbol.strip().lower() + ".us"
    url = f"https://stooq.com/q/l/?s={ticker}&i=d"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        frame = pd.read_csv(StringIO(response.text))
        if frame.empty:
            return None

        close_column = "Close" if "Close" in frame.columns else "close"
        price = frame.iloc[0].get(close_column)
        if pd.isna(price):
            return None
        return float(price)
    except (requests.RequestException, ValueError, pd.errors.ParserError):
        return None
