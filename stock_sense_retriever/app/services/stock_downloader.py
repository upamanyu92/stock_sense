import yfinance as yf
from typing import List
from app.models.stock import StockData


def download_stock_data(symbol: str, start_date: str, end_date: str) -> List[StockData]:
    data = yf.download(symbol, start=start_date, end=end_date)
    if data.empty:
        return []

    stock_data_list = [
        StockData(
            date=index,
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
            volume=row['Volume']
        )
        for index, row in data.iterrows()
    ]
    return stock_data_list
