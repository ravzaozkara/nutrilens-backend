from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.orm import Session
import os

from . import models
from .database import get_db
from .limiter import limiter
from .routers import auth, analyze, meals
from .nutrition import NUTRITION_DB

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tables are managed by Alembic; nothing to do here.
    yield


app = FastAPI(
    title="NutriLens API",
    description="Yapay Zeka Destekli Kişiselleştirilmiş Beslenme Asistanı",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded food images as static files at /uploads/<filename>
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(meals.router)


@app.get("/")
def health_check(db: Session = Depends(get_db)):
    # DB probe — must not raise; catch everything
    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:
        database_status = "disconnected"

    from .core.config import settings
    ai_model_status = "loaded" if os.path.exists(settings.MODEL_PATH) else "simulation"

    return {
        "status": "ok",
        "database": database_status,
        "ai_model": ai_model_status,
        "version": "1.0.0",
    }


@app.get("/setup-database")
def setup_database(db: Session = Depends(get_db)):
    """Veritabanını 30 Türk yemeği ile başlatır."""
    food_list = [
        # ÇORBALAR
        models.Food(name="Mercimek Çorbası", calories=65, is_risky_for_diabetic=False, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Besleyici ve sağlıklı."),
        models.Food(name="Yoğurt Çorbası", calories=55, is_risky_for_diabetic=False, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=True, warning_message="Hafif ve sindirimi kolay. Un içerebilir."),
        models.Food(name="Domates Çorbası", calories=45, is_risky_for_diabetic=False, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Düşük kalorili."),
        models.Food(name="Tarhana Çorbası", calories=70, is_risky_for_diabetic=False, is_risky_for_hypertensive=True, is_risky_for_cholesterol=False, is_risky_for_celiac=True, warning_message="Tuz içeriğine dikkat. Un içerir."),
        # ANA YEMEKLER
        models.Food(name="Kuru Fasulye", calories=120, is_risky_for_diabetic=False, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Yüksek lif kaynağı."),
        models.Food(name="Karnıyarık", calories=135, is_risky_for_diabetic=False, is_risky_for_hypertensive=True, is_risky_for_cholesterol=True, is_risky_for_celiac=False, warning_message="Kızartma yağı nedeniyle ağır olabilir."),
        models.Food(name="Bulgur Pilavı", calories=105, is_risky_for_diabetic=True, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Karbonhidrat içeriğine dikkat."),
        models.Food(name="Pirinç Pilavı", calories=130, is_risky_for_diabetic=True, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Glisemik indeksi yüksektir."),
        models.Food(name="Köfte", calories=220, is_risky_for_diabetic=False, is_risky_for_hypertensive=True, is_risky_for_cholesterol=True, is_risky_for_celiac=False, warning_message="Yüksek yağ içerir."),
        models.Food(name="Makarna", calories=155, is_risky_for_diabetic=True, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=True, warning_message="Yüksek karbonhidrat. Glüten içerir."),
        models.Food(name="Mantı", calories=175, is_risky_for_diabetic=True, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=True, warning_message="Yüksek karbonhidrat. Hamur içerir."),
        models.Food(name="Lahmacun", calories=210, is_risky_for_diabetic=True, is_risky_for_hypertensive=True, is_risky_for_cholesterol=False, is_risky_for_celiac=True, warning_message="Tuz ve karbonhidrat yüksek. Hamur içerir."),
        models.Food(name="Yeşil Biber Dolması", calories=95, is_risky_for_diabetic=False, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Hafif ve besleyici."),
        models.Food(name="Fırında Tavuk", calories=190, is_risky_for_diabetic=False, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Yüksek protein kaynağı."),
        models.Food(name="Adana Kebap", calories=245, is_risky_for_diabetic=False, is_risky_for_hypertensive=True, is_risky_for_cholesterol=True, is_risky_for_celiac=False, warning_message="Yüksek yağ ve sodyum."),
        models.Food(name="Sarma", calories=140, is_risky_for_diabetic=True, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Pirinç içeriği nedeniyle ölçülü tüketilmeli."),
        # KAHVALTILIK
        models.Food(name="Menemen", calories=110, is_risky_for_diabetic=False, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Protein deposu."),
        models.Food(name="Sucuklu Yumurta", calories=250, is_risky_for_diabetic=False, is_risky_for_hypertensive=True, is_risky_for_cholesterol=True, is_risky_for_celiac=False, warning_message="İşlenmiş et ve yüksek tuz."),
        models.Food(name="Simit", calories=285, is_risky_for_diabetic=True, is_risky_for_hypertensive=True, is_risky_for_cholesterol=False, is_risky_for_celiac=True, warning_message="Yüksek karbonhidrat. Glüten içerir."),
        models.Food(name="Poğaça", calories=340, is_risky_for_diabetic=True, is_risky_for_hypertensive=True, is_risky_for_cholesterol=True, is_risky_for_celiac=True, warning_message="Yüksek yağ ve karbonhidrat. Glüten içerir."),
        models.Food(name="Gözleme", calories=220, is_risky_for_diabetic=True, is_risky_for_hypertensive=False, is_risky_for_cholesterol=True, is_risky_for_celiac=True, warning_message="Hamur bazlı. Glüten içerir."),
        models.Food(name="Börek", calories=310, is_risky_for_diabetic=True, is_risky_for_hypertensive=True, is_risky_for_cholesterol=True, is_risky_for_celiac=True, warning_message="Yüksek yağ ve karbonhidrat. Hamur içerir."),
        models.Food(name="Beyaz Peynir", calories=260, is_risky_for_diabetic=False, is_risky_for_hypertensive=True, is_risky_for_cholesterol=True, is_risky_for_celiac=False, warning_message="Yüksek sodyum ve doymuş yağ."),
        # TATLILAR
        models.Food(name="Baklava", calories=428, is_risky_for_diabetic=True, is_risky_for_hypertensive=False, is_risky_for_cholesterol=True, is_risky_for_celiac=True, warning_message="Aşırı şeker içerir. Hamur ve tereyağı bazlı."),
        models.Food(name="Sütlaç", calories=130, is_risky_for_diabetic=True, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Şeker içeriğine dikkat."),
        models.Food(name="Künefe", calories=390, is_risky_for_diabetic=True, is_risky_for_hypertensive=True, is_risky_for_cholesterol=True, is_risky_for_celiac=True, warning_message="Hem şeker hem yağ deposu. Kadayıf hamuru içerir."),
        models.Food(name="Kazandibi", calories=145, is_risky_for_diabetic=True, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Şeker içeriğine dikkat."),
        # SALATALAR VE YANLAR
        models.Food(name="Çoban Salatası", calories=35, is_risky_for_diabetic=False, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Düşük kalorili ve sağlıklı."),
        models.Food(name="Cacık", calories=40, is_risky_for_diabetic=False, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=False, warning_message="Hafif ve serinletici."),
        models.Food(name="Kısır", calories=130, is_risky_for_diabetic=False, is_risky_for_hypertensive=False, is_risky_for_cholesterol=False, is_risky_for_celiac=True, warning_message="Bulgur bazlı. Glüten duyarlılığı olanlara dikkat."),
    ]

    for food in food_list:
        existing = db.query(models.Food).filter(models.Food.name == food.name).first()
        if not existing:
            db.add(food)

    db.commit()
    return {"message": f"{len(food_list)} yemeklik liste başarıyla yüklendi!"}
