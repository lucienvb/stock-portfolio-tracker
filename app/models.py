from sqlalchemy import Column, Float, Integer, String

from app.database import Base


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(12), nullable=False, index=True)
    shares = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
