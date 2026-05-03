def test_create_meal(client, auth_headers):
    meal_data = {
        "food_label": "Mercimek Çorbası",
        "calories": 65,
        "protein": 4.2,
        "carbs": 9.8,
        "fat": 1.5,
        "health_warnings": "",
    }
    response = client.post("/meals/", json=meal_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["food_label"] == "Mercimek Çorbası"
    assert data["calories"] == 65
    assert "id" in data
    assert "created_at" in data


def test_list_meals(client, auth_headers):
    # Önce bir öğün oluştur
    client.post(
        "/meals/",
        json={"food_label": "Baklava", "calories": 428, "protein": 7.9, "carbs": 46.2, "fat": 24.5},
        headers=auth_headers,
    )
    response = client.get("/meals/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["food_label"] == "Baklava"


def test_list_meals_empty(client, auth_headers):
    response = client.get("/meals/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_meal_summary(client, auth_headers):
    # İki öğün oluştur
    client.post(
        "/meals/",
        json={"food_label": "Mercimek Çorbası", "calories": 65, "protein": 4.2, "carbs": 9.8, "fat": 1.5},
        headers=auth_headers,
    )
    client.post(
        "/meals/",
        json={"food_label": "Baklava", "calories": 428, "protein": 7.9, "carbs": 46.2, "fat": 24.5},
        headers=auth_headers,
    )
    response = client.get("/meals/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["meal_count"] == 2
    assert data["total_calories"] == 493


def test_delete_meal(client, auth_headers):
    # Öğün oluştur
    create_response = client.post(
        "/meals/",
        json={"food_label": "Cacık", "calories": 40, "protein": 2.5, "carbs": 3.0, "fat": 2.0},
        headers=auth_headers,
    )
    meal_id = create_response.json()["id"]

    # Sil
    response = client.delete(f"/meals/{meal_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "silindi" in response.json()["message"]

    # Silindikten sonra listede olmamalı
    list_response = client.get("/meals/", headers=auth_headers)
    assert len(list_response.json()) == 0


def test_delete_meal_not_found(client, auth_headers):
    response = client.delete("/meals/9999", headers=auth_headers)
    assert response.status_code == 404


def test_meals_unauthorized(client):
    response = client.get("/meals/")
    assert response.status_code == 401


# ── /meals/weekly-summary ─────────────────────────────────────────────────────

def test_weekly_summary_empty(client, auth_headers):
    response = client.get("/meals/weekly-summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    for day in data:
        assert day["meal_count"] == 0
        assert day["total_calories"] == 0.0
        assert "date" in day


def test_weekly_summary_with_meal(client, auth_headers):
    client.post(
        "/meals/",
        json={"food_label": "Mercimek Çorbası", "calories": 65, "protein": 4.2, "carbs": 9.8, "fat": 1.5},
        headers=auth_headers,
    )
    response = client.get("/meals/weekly-summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    today_entry = data[-1]
    assert today_entry["meal_count"] == 1
    assert today_entry["total_calories"] == 65.0


def test_weekly_summary_unauthorized(client):
    response = client.get("/meals/weekly-summary")
    assert response.status_code == 401
