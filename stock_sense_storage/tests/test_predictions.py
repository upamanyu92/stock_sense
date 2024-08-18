def test_get_all_predictions(client):
    response = client.get('/api/predictions/')
    assert response.status_code == 200
