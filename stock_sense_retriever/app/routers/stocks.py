from fastapi import APIRouter, HTTPException
from app.models.stock import StockRequest, StockData
from app.services.stock_downloader import download_stock_data
from typing import List

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"]
)


@router.post("/download", response_model=List[StockData])
def download_stock(request: StockRequest):
    stock_data = download_stock_data(request.symbol, request.start_date, request.end_date)

    if not stock_data:
        raise HTTPException(status_code=404, detail="No data found for the specified date range.")

    return stock_data
