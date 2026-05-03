# FastAPI Stock Portfolio Tracker

Small FastAPI service for tracking stock holdings and calculating portfolio value.

## Intentional legacy dependency setup

This project intentionally pins older versions to help test dependency update automation:

- `fastapi==0.115.0` (updated to support Pydantic v2)
- `pydantic==2.13.3`
- `requests==2.28.2`
- `SQLAlchemy==1.4.49` (1.x line)
- `pandas==1.5.3`
- `numpy==1.24.4` (pinned to match `pandas==1.5.3` ABI expectations)
- `httpx==0.27.2` (for FastAPI/Starlette test client)
- `pytest==8.3.5`

## Setup

```bash
brew install python@3.10
rm -rf .venv
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade "pip<26" "setuptools<81" wheel
pip install -r requirements.txt
```

If you previously installed with a different dependency graph, force reinstall once:

```bash
pip install --force-reinstall -r requirements.txt
```

If you had old FastAPI/Pydantic v1 packages installed before this migration, a clean reinstall is safest:

```bash
rm -rf .venv
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade "pip<26" "setuptools<81" wheel
pip install -r requirements.txt
```

If tests fail with `ModuleNotFoundError: No module named 'httpx'`, reinstall deps in the active venv:

```bash
pip install --force-reinstall -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Run tests

```bash
PYTHONPATH=. pytest -v tests
```

The repository includes both unit and integration tests and now runs them with `pytest`.

## API quickstart

- `GET /health`
- `POST /holdings`
- `GET /holdings`
- `PUT /holdings/{holding_id}`
- `DELETE /holdings/{holding_id}`
- `GET /portfolio/value`

Example create payload:

```json
{
  "symbol": "AAPL",
  "shares": 10,
  "purchase_price": 170.5
}
```

## Curl commands to test all API routes

```bash
BASE_URL="http://127.0.0.1:8000"

# Health
curl -sS "$BASE_URL/health"

# List holdings (initially empty)
curl -sS "$BASE_URL/holdings"

# Create holding #1
curl -sS -X POST "$BASE_URL/holdings" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","shares":10,"purchase_price":170.5}'

# Create holding #2
curl -sS -X POST "$BASE_URL/holdings" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"MSFT","shares":5,"purchase_price":300}'

# List holdings
curl -sS "$BASE_URL/holdings"

# Update holding id 1
curl -sS -X PUT "$BASE_URL/holdings/1" \
  -H "Content-Type: application/json" \
  -d '{"shares":12,"purchase_price":165}'

# Portfolio valuation
curl -sS "$BASE_URL/portfolio/value"

# Delete holding id 2 (expect HTTP 204)
curl -sS -o /dev/null -w "%{http_code}\n" -X DELETE "$BASE_URL/holdings/2"

# Error path examples
curl -sS -X PUT "$BASE_URL/holdings/999" \
  -H "Content-Type: application/json" \
  -d '{"shares":1}'
curl -sS -X DELETE "$BASE_URL/holdings/999"
```

Notes:

- SQLite database file is created as `portfolio.db` in the project root.
- Portfolio valuation attempts to fetch latest prices from Stooq and falls back to `purchase_price` if unavailable.
