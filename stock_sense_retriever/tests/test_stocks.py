from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_download_stock():
    response = client.post(
        "/stocks/download",
        json={
            "symbol": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-01-10"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) > 0
