def test_analyze_text_known_food(client, auth_headers):
    response = client.post(
        "/analyze",
        params={"food_name": "mercimek_corbasi"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["food_name"] == "Mercimek Çorbası"
    assert data["calories"] == 65
    assert data["protein"] > 0
    assert data["confidence"] == 1.0


def test_analyze_text_turkish_name(client, auth_headers):
    response = client.post(
        "/analyze",
        params={"food_name": "Baklava"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["calories"] == 428


def test_analyze_text_unknown_food(client, auth_headers):
    response = client.post(
        "/analyze",
        params={"food_name": "bilinmeyen_yemek"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["calories"] == 0
    assert "kayıtlı değil" in data["health_warning"]


def test_analyze_text_unauthorized(client):
    response = client.post("/analyze", params={"food_name": "baklava"})
    assert response.status_code == 401


def test_analyze_image_valid(client, auth_headers, test_image):
    response = client.post(
        "/analyze-image",
        files={"file": ("test.jpg", test_image, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "food_name" in data
    assert "confidence" in data
    assert "image_path" in data
    assert data["image_path"].endswith(".jpg")


def test_analyze_image_invalid_format(client, auth_headers):
    response = client.post(
        "/analyze-image",
        files={"file": ("test.txt", b"not an image", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "Desteklenmeyen" in response.json()["detail"]


def test_analyze_image_unauthorized(client, test_image):
    response = client.post(
        "/analyze-image",
        files={"file": ("test.jpg", test_image, "image/jpeg")},
    )
    assert response.status_code == 401


def test_analyze_diabetic_warning(client, auth_headers):
    """Diyabetli kullanıcı baklava analiz ettiğinde uyarı almalı."""
    response = client.post(
        "/analyze",
        params={"food_name": "baklava"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "karbonhidrat" in data["health_warning"].lower() or "diyabet" in data["health_warning"].lower()
