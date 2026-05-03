def test_register_success(client, test_user_data):
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["is_diabetic"] == test_user_data["is_diabetic"]
    assert data["is_kidney_disease"] == test_user_data["is_kidney_disease"]
    assert "id" in data


def test_register_duplicate_email(client, test_user_data, registered_user):
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert "zaten kayıtlı" in response.json()["detail"]


# ── /auth/login (JSON) ────────────────────────────────────────────────────────

def test_login_json_success(client, registered_user, test_user_data):
    response = client.post(
        "/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_json_wrong_password(client, registered_user, test_user_data):
    response = client.post(
        "/auth/login",
        json={"email": test_user_data["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_json_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@test.com", "password": "test123"},
    )
    assert response.status_code == 401


# ── /auth/token (OAuth2 form — kept for /docs) ────────────────────────────────

def test_login_form_success(client, registered_user, test_user_data):
    response = client.post(
        "/auth/token",
        data={"username": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_form_wrong_password(client, registered_user, test_user_data):
    response = client.post(
        "/auth/token",
        data={"username": test_user_data["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401


# ── /auth/me ──────────────────────────────────────────────────────────────────

def test_get_me(client, auth_headers, test_user_data):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["is_diabetic"] is True
    assert "health_conditions" in data
    assert "diabetes" in data["health_conditions"]


def test_get_me_unauthorized(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


# ── /auth/profile ─────────────────────────────────────────────────────────────

def test_update_profile_name(client, auth_headers):
    response = client.put(
        "/auth/profile",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_update_profile_height(client, auth_headers):
    response = client.put(
        "/auth/profile",
        json={"height_cm": 180.0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["height_cm"] == 180.0


def test_update_profile_health_conditions_derived(client, auth_headers):
    response = client.put(
        "/auth/profile",
        json={"is_diabetic": True, "is_hypertensive": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "diabetes" in data["health_conditions"]
    assert "hypertension" in data["health_conditions"]


def test_update_profile_invalid_birth_date(client, auth_headers):
    response = client.put(
        "/auth/profile",
        json={"birth_date": "1800-01-01"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_update_profile_future_birth_date(client, auth_headers):
    response = client.put(
        "/auth/profile",
        json={"birth_date": "2099-12-31"},
        headers=auth_headers,
    )
    assert response.status_code == 422


# ── /auth/password ────────────────────────────────────────────────────────────

def test_change_password_success(client, auth_headers, test_user_data):
    response = client.put(
        "/auth/password",
        json={"current_password": test_user_data["password"], "new_password": "NewPass9999!"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Yeni şifreyle giriş çalışmalı
    login_resp = client.post(
        "/auth/login",
        json={"email": test_user_data["email"], "password": "NewPass9999!"},
    )
    assert login_resp.status_code == 200


def test_change_password_wrong_current(client, auth_headers):
    response = client.put(
        "/auth/password",
        json={"current_password": "totally_wrong", "new_password": "NewPass9999!"},
        headers=auth_headers,
    )
    assert response.status_code == 401
