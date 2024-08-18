def test_get_all_stock_quotes(client):
    response = client.get('/api/stock_quotes/')
    assert response.status_code == 200
