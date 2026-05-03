import os
from PIL import Image

from .core.config import settings
from .nutrition import CLASS_NAMES, get_display_name

_model = None


def load_model():
    """
    EfficientNet-B0 modelini yükler.
    Model dosyası yoksa None döndürür (simülasyon moduna geçilir).
    """
    global _model
    if _model is not None:
        return _model

    if not os.path.exists(settings.MODEL_PATH):
        return None

    try:
        import torch
        from torchvision.models import efficientnet_b0

        model = efficientnet_b0(weights=None)
        num_classes = len(CLASS_NAMES)
        model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, num_classes)
        model.load_state_dict(torch.load(settings.MODEL_PATH, map_location="cpu"))
        model.eval()
        _model = model
        return _model
    except Exception:
        return None


def get_transform():
    """ImageNet normalizasyonu ile görüntü dönüşüm pipeline'ı."""
    from torchvision import transforms

    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
    ])


def predict_food(image_path: str) -> dict:
    """
    Yüklenen görselden yemek tahmini yapar.

    Döndürür:
        {
            "food_key": str,         # snake_case yemek anahtarı
            "display_name": str,     # Türkçe gösterim adı
            "confidence": float,     # Güven skoru (0.0 - 1.0)
            "is_confident": bool     # Eşiği geçip geçmediği
        }
    """
    model = load_model()

    if model is None:
        return _simulate_prediction(image_path)

    import torch

    img = Image.open(image_path).convert("RGB")
    transform = get_transform()
    img_tensor = transform(img).unsqueeze(0)  # Batch boyutu ekle

    with torch.no_grad():
        output = model(img_tensor)
        probabilities = torch.nn.functional.softmax(output, dim=1)
        confidence, predicted_index = torch.max(probabilities, 1)
        confidence = confidence.item()
        predicted_index = predicted_index.item()

    food_key = CLASS_NAMES[predicted_index] if predicted_index < len(CLASS_NAMES) else "bilinmeyen"

    return {
        "food_key": food_key,
        "display_name": get_display_name(food_key),
        "confidence": round(confidence, 4),
        "is_confident": confidence >= settings.CONFIDENCE_THRESHOLD
    }


def _simulate_prediction(image_path: str) -> dict:
    """
    Model dosyası mevcut olmadığında kullanılan simülasyon.
    Görselin geçerli olduğunu doğrular ve rastgele bir tahmin döndürür.
    """
    import random

    try:
        img = Image.open(image_path)
        img.verify()
    except Exception:
        return {
            "food_key": "bilinmeyen",
            "display_name": "Geçersiz Görsel",
            "confidence": 0.0,
            "is_confident": False
        }

    food_key = random.choice(CLASS_NAMES)
    confidence = round(random.uniform(0.40, 0.95), 4)

    return {
        "food_key": food_key,
        "display_name": get_display_name(food_key),
        "confidence": confidence,
        "is_confident": confidence >= settings.CONFIDENCE_THRESHOLD
    }
