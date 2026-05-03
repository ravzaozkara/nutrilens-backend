import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# SQLite in-memory test veritabanı
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Her test öncesi tabloları oluştur, sonra temizle."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user_data():
    return {
        "email": "test@nutrilens.com",
        "password": "test123456",
        "is_diabetic": True,
        "is_hypertensive": False,
        "is_kidney_disease": False,
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Kayıtlı bir test kullanıcısı oluşturur."""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def auth_headers(client, registered_user, test_user_data):
    """Kimlik doğrulaması yapılmış Authorization header döndürür (JSON login)."""
    response = client.post(
        "/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_image():
    """Test için küçük bir JPEG görsel oluşturur."""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer
