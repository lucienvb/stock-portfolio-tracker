from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db
from app.services import fetch_latest_price

app = FastAPI(title="Stock Portfolio Tracker")

Base.metadata.create_all(bind=engine)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/holdings", response_model=schemas.HoldingResponse, status_code=status.HTTP_201_CREATED)
def create_holding(payload: schemas.HoldingCreate, db: Session = Depends(get_db)):
    holding = models.Holding(
        symbol=payload.symbol.upper(),
        shares=payload.shares,
        purchase_price=payload.purchase_price,
    )
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


@app.get("/holdings", response_model=List[schemas.HoldingResponse])
def list_holdings(db: Session = Depends(get_db)):
    return db.query(models.Holding).order_by(models.Holding.id.asc()).all()


@app.put("/holdings/{holding_id}", response_model=schemas.HoldingResponse)
def update_holding(holding_id: int, payload: schemas.HoldingUpdate, db: Session = Depends(get_db)):
    holding = db.query(models.Holding).filter(models.Holding.id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")

    if payload.symbol is not None:
        holding.symbol = payload.symbol.upper()
    if payload.shares is not None:
        holding.shares = payload.shares
    if payload.purchase_price is not None:
        holding.purchase_price = payload.purchase_price

    db.commit()
    db.refresh(holding)
    return holding


@app.delete("/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(holding_id: int, db: Session = Depends(get_db)):
    holding = db.query(models.Holding).filter(models.Holding.id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")

    db.delete(holding)
    db.commit()
    return None


@app.get("/portfolio/value", response_model=schemas.PortfolioValueResponse)
def get_portfolio_value(db: Session = Depends(get_db)):
    holdings = db.query(models.Holding).all()
    valuation_items = []
    total_market_value = 0.0
    total_cost_basis = 0.0

    for holding in holdings:
        latest_price = fetch_latest_price(holding.symbol)
        if latest_price is None:
            latest_price = holding.purchase_price

        market_value = latest_price * holding.shares
        cost_basis = holding.purchase_price * holding.shares
        gain_loss = market_value - cost_basis

        total_market_value += market_value
        total_cost_basis += cost_basis

        valuation_items.append(
            schemas.HoldingValuation(
                id=holding.id,
                symbol=holding.symbol,
                shares=holding.shares,
                latest_price=round(latest_price, 2),
                market_value=round(market_value, 2),
                cost_basis=round(cost_basis, 2),
                gain_loss=round(gain_loss, 2),
            )
        )

    return schemas.PortfolioValueResponse(
        total_market_value=round(total_market_value, 2),
        total_cost_basis=round(total_cost_basis, 2),
        total_gain_loss=round(total_market_value - total_cost_basis, 2),
        holdings=valuation_items,
    )
