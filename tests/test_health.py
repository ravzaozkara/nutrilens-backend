def test_health_check_shape(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert data["database"] in ("connected", "disconnected")
    assert data["ai_model"] in ("loaded", "simulation")


def test_health_check_database_connected(client):
    # Tests always use a live SQLite session, so DB should be reachable.
    response = client.get("/")
    assert response.json()["database"] == "connected"


def test_health_check_ai_model_simulation(client):
    # food_model.pt is never present in CI / test environments.
    response = client.get("/")
    assert response.json()["ai_model"] == "simulation"


def test_health_check_no_auth_required(client):
    # Endpoint must be reachable without a token.
    response = client.get("/")
    assert response.status_code == 200
