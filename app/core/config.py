import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql://postgres:123456@localhost:5433/nutrilens"
    SECRET_KEY: str = "nutrilens_gizli_anahtar_buraya"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "..", "..", "model", "best_model_final.pth")
    CONFIDENCE_THRESHOLD: float = 0.50
    MAX_IMAGE_SIZE_MB: int = 10


settings = Settings()
