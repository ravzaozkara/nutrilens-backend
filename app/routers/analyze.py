import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..ai_model import predict_food
from ..nutrition import get_nutrition, build_health_warnings, NUTRITION_DB
from ..core.config import settings

router = APIRouter(tags=["analyze"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _lookup_by_display_name(food_name: str) -> str | None:
    """Türkçe yemek adından snake_case anahtarını bulur."""
    for key, data in NUTRITION_DB.items():
        if data["display_name"].lower() == food_name.lower():
            return key
    return None


@router.post("/analyze", response_model=schemas.AnalysisResult)
def analyze_food(
    food_name: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Önce TurKomp veritabanında ara (snake_case veya Türkçe isim)
    food_key = food_name if food_name in NUTRITION_DB else _lookup_by_display_name(food_name)

    if food_key and food_key in NUTRITION_DB:
        nutrition = NUTRITION_DB[food_key]
        warnings = build_health_warnings(
            food_key,
            is_diabetic=user.is_diabetic,
            is_hypertensive=user.is_hypertensive,
            is_kidney_disease=user.is_kidney_disease,
        )
        health_warning = nutrition.get("display_name", food_name) + " - besin bilgileri mevcut."
        if warnings:
            health_warning = " ".join(warnings)

        return {
            "food_name": nutrition["display_name"],
            "confidence": 1.0,
            "health_warning": health_warning,
            "calories": nutrition["calories"],
            "protein": nutrition["protein"],
            "carbs": nutrition["carbs"],
            "fat": nutrition["fat"],
        }

    # TurKomp'ta yoksa DB Food tablosuna bak (eski yemekler için geriye uyumluluk)
    food_item = db.query(models.Food).filter(models.Food.name == food_name).first()
    if food_item:
        return {
            "food_name": food_item.name,
            "confidence": 0.99,
            "health_warning": food_item.warning_message,
            "calories": food_item.calories,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
        }

    return {
        "food_name": food_name,
        "confidence": 0.0,
        "health_warning": "Bu yemek henüz veri tabanımızda kayıtlı değil.",
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
    }


@router.post("/analyze-image", response_model=schemas.ImageAnalysisResult)
def analyze_food_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Yüklenen yemek fotoğrafını AI modeli ile analiz eder.
    1. Görsel doğrulanır ve uploads/ klasörüne kaydedilir
    2. EfficientNet-B0 modeli görseli analiz eder
    3. Güven skoru kontrolü yapılır
    4. TurKomp veritabanından besin bilgileri çekilir
    5. Kişiselleştirilmiş sağlık uyarıları oluşturulur
    """
    # Dosya türü kontrolü
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Desteklenmeyen dosya formatı. Lütfen JPEG, PNG veya WebP formatında yükleyin."
        )

    # Dosya boyutu kontrolü
    content = file.file.read()
    max_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"Dosya boyutu çok büyük. Maksimum {settings.MAX_IMAGE_SIZE_MB}MB kabul edilmektedir."
        )

    # Görseli benzersiz isimle kaydet
    file_ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # AI Modeline gönder
    prediction = predict_food(file_path)

    food_key = prediction["food_key"]
    display_name = prediction["display_name"]
    confidence = prediction["confidence"]

    # Güven skoru kontrolü
    if not prediction["is_confident"]:
        return {
            "food_name": display_name,
            "confidence": confidence,
            "health_warning": (
                f"Yemek net olarak tanımlanamadı (güven skoru: %{int(confidence * 100)}). "
                f"Lütfen daha net bir fotoğraf çekip tekrar deneyin. "
                f"Minimum güven eşiği: %{int(settings.CONFIDENCE_THRESHOLD * 100)}"
            ),
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "image_path": unique_filename,
        }

    # TurKomp besin bilgilerini çek
    nutrition = get_nutrition(food_key)

    if not nutrition:
        return {
            "food_name": display_name,
            "confidence": confidence,
            "health_warning": "Yemek tanındı ancak besin bilgisi bulunamadı.",
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "image_path": unique_filename,
        }

    # Kişiselleştirilmiş sağlık uyarıları
    warnings = build_health_warnings(
        food_key,
        is_diabetic=user.is_diabetic,
        is_hypertensive=user.is_hypertensive,
        is_kidney_disease=user.is_kidney_disease,
    )

    health_warning = f"{display_name} başarıyla tanındı."
    if warnings:
        health_warning = " ".join(warnings)

    return {
        "food_name": display_name,
        "confidence": confidence,
        "health_warning": health_warning,
        "calories": nutrition["calories"],
        "protein": nutrition["protein"],
        "carbs": nutrition["carbs"],
        "fat": nutrition["fat"],
        "image_path": unique_filename,
    }
