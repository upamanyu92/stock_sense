from pydantic import BaseModel
from datetime import date

class StockRequest(BaseModel):
    symbol: str
    start_date: date
    end_date: date

class StockData(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
