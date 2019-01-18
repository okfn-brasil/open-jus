def test_home(client):
    assert client.get('/').status_code == 200
