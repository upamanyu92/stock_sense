from fastapi import FastAPI
from app.routers import stocks

app = FastAPI(
    title="Stock Data Downloader Microservice",
    version="1.0.0"
)

app.include_router(stocks.router)

@app.get("/")
def root():
    return {"message": "Stock Data Downloader Microservice is running"}
