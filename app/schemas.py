from typing import List, Optional

from pydantic import BaseModel, Field


class HoldingBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=12)
    shares: float = Field(..., gt=0)
    purchase_price: float = Field(..., gt=0)


class HoldingCreate(HoldingBase):
    pass


class HoldingUpdate(BaseModel):
    symbol: Optional[str] = Field(default=None, min_length=1, max_length=12)
    shares: Optional[float] = Field(default=None, gt=0)
    purchase_price: Optional[float] = Field(default=None, gt=0)


class HoldingResponse(HoldingBase):
    id: int

    class Config:
        orm_mode = True


class HoldingValuation(BaseModel):
    id: int
    symbol: str
    shares: float
    latest_price: float
    market_value: float
    cost_basis: float
    gain_loss: float


class PortfolioValueResponse(BaseModel):
    total_market_value: float
    total_cost_basis: float
    total_gain_loss: float
    holdings: List[HoldingValuation]
