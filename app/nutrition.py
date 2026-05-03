# TurKomp (TÜBİTAK) Besin Veritabanı ve Sağlık Uyarı Motoru
# 30 Türk yemeği için 100 gram başına besin değerleri

# Model çıkış sınıfları (eğitim sırasına göre, snake_case)
CLASS_NAMES = [
    # Ana Yemekler (12)
    "kuru_fasulye", "karniyanik", "bulgur_pilavi", "pirinc_pilavi",
    "kofte", "makarna", "manti", "lahmacun", "yesil_biber_dolmasi",
    "firinda_tavuk", "adana_kebap", "sarma",
    # Çorbalar (4)
    "mercimek_corbasi", "yogurt_corbasi", "domates_corbasi", "tarhana_corbasi",
    # Kahvaltılık (7)
    "menemen", "sucuklu_yumurta", "simit", "pogaca", "gozleme", "borek", "beyaz_peynir",
    # Tatlılar (4)
    "baklava", "sutlac", "kunefe", "kazandibi",
    # Salatalar ve Yanlar (3)
    "coban_salata", "cacik", "kisir"
]

# 100 gram başına besin değerleri (TurKomp referanslı yaklaşık değerler)
NUTRITION_DB = {
    # === ANA YEMEKLER ===
    "kuru_fasulye": {
        "display_name": "Kuru Fasulye",
        "calories": 120, "protein": 8.5, "carbs": 18.0, "fat": 1.8
    },
    "karniyanik": {
        "display_name": "Karnıyarık",
        "calories": 135, "protein": 6.2, "carbs": 8.5, "fat": 9.0
    },
    "bulgur_pilavi": {
        "display_name": "Bulgur Pilavı",
        "calories": 105, "protein": 3.5, "carbs": 20.0, "fat": 1.5
    },
    "pirinc_pilavi": {
        "display_name": "Pirinç Pilavı",
        "calories": 130, "protein": 2.5, "carbs": 28.0, "fat": 1.2
    },
    "kofte": {
        "display_name": "Köfte",
        "calories": 220, "protein": 15.0, "carbs": 8.0, "fat": 14.5
    },
    "makarna": {
        "display_name": "Makarna",
        "calories": 155, "protein": 5.5, "carbs": 30.0, "fat": 1.5
    },
    "manti": {
        "display_name": "Mantı",
        "calories": 175, "protein": 8.0, "carbs": 22.0, "fat": 6.5
    },
    "lahmacun": {
        "display_name": "Lahmacun",
        "calories": 210, "protein": 9.5, "carbs": 25.0, "fat": 8.0
    },
    "yesil_biber_dolmasi": {
        "display_name": "Yeşil Biber Dolması",
        "calories": 95, "protein": 3.8, "carbs": 12.0, "fat": 3.5
    },
    "firinda_tavuk": {
        "display_name": "Fırında Tavuk",
        "calories": 190, "protein": 25.0, "carbs": 0.5, "fat": 9.5
    },
    "adana_kebap": {
        "display_name": "Adana Kebap",
        "calories": 245, "protein": 18.0, "carbs": 2.0, "fat": 18.5
    },
    "sarma": {
        "display_name": "Sarma (Yaprak Sarma)",
        "calories": 140, "protein": 3.0, "carbs": 15.0, "fat": 7.5
    },

    # === ÇORBALAR ===
    "mercimek_corbasi": {
        "display_name": "Mercimek Çorbası",
        "calories": 65, "protein": 4.2, "carbs": 9.8, "fat": 1.5
    },
    "yogurt_corbasi": {
        "display_name": "Yoğurt Çorbası (Yayla)",
        "calories": 55, "protein": 2.5, "carbs": 6.0, "fat": 2.5
    },
    "domates_corbasi": {
        "display_name": "Domates Çorbası",
        "calories": 45, "protein": 1.2, "carbs": 7.5, "fat": 1.5
    },
    "tarhana_corbasi": {
        "display_name": "Tarhana Çorbası",
        "calories": 70, "protein": 2.8, "carbs": 11.0, "fat": 1.8
    },

    # === KAHVALTILIK ===
    "menemen": {
        "display_name": "Menemen",
        "calories": 110, "protein": 6.5, "carbs": 5.0, "fat": 7.5
    },
    "sucuklu_yumurta": {
        "display_name": "Sucuklu Yumurta",
        "calories": 250, "protein": 14.0, "carbs": 1.5, "fat": 21.0
    },
    "simit": {
        "display_name": "Simit",
        "calories": 285, "protein": 9.0, "carbs": 52.0, "fat": 4.5
    },
    "pogaca": {
        "display_name": "Poğaça",
        "calories": 340, "protein": 6.5, "carbs": 38.0, "fat": 18.0
    },
    "gozleme": {
        "display_name": "Gözleme",
        "calories": 220, "protein": 7.0, "carbs": 28.0, "fat": 9.0
    },
    "borek": {
        "display_name": "Börek",
        "calories": 310, "protein": 8.5, "carbs": 30.0, "fat": 18.0
    },
    "beyaz_peynir": {
        "display_name": "Beyaz Peynir",
        "calories": 260, "protein": 17.0, "carbs": 1.0, "fat": 21.0
    },

    # === TATLILAR ===
    "baklava": {
        "display_name": "Baklava",
        "calories": 428, "protein": 7.9, "carbs": 46.2, "fat": 24.5
    },
    "sutlac": {
        "display_name": "Sütlaç",
        "calories": 130, "protein": 3.5, "carbs": 22.0, "fat": 3.0
    },
    "kunefe": {
        "display_name": "Künefe",
        "calories": 390, "protein": 8.0, "carbs": 45.0, "fat": 20.0
    },
    "kazandibi": {
        "display_name": "Kazandibi",
        "calories": 145, "protein": 4.0, "carbs": 24.0, "fat": 3.5
    },

    # === SALATALAR VE YANLAR ===
    "coban_salata": {
        "display_name": "Çoban Salatası",
        "calories": 35, "protein": 1.0, "carbs": 5.5, "fat": 1.0
    },
    "cacik": {
        "display_name": "Cacık",
        "calories": 40, "protein": 2.5, "carbs": 3.0, "fat": 2.0
    },
    "kisir": {
        "display_name": "Kısır",
        "calories": 130, "protein": 3.5, "carbs": 20.0, "fat": 4.0
    },
}


# Hastalık bazlı sağlık uyarıları
DISEASE_WARNINGS = {
    "diabetes": {
        "risky_foods": [
            "baklava", "sutlac", "kazandibi", "pirinc_pilavi", "makarna",
            "kunefe", "simit", "pogaca", "gozleme", "borek", "manti",
            "bulgur_pilavi", "sarma", "lahmacun"
        ],
        "threshold_carbs_g": 60,
        "message": "Bu yemek yüksek karbonhidrat içermektedir. Diyabet yönetiminiz için porsiyon kontrolüne dikkat edin."
    },
    "hypertension": {
        "risky_foods": [
            "sucuklu_yumurta", "borek", "pogaca", "beyaz_peynir",
            "tarhana_corbasi", "lahmacun", "adana_kebap", "kofte",
            "simit"
        ],
        "message": "Bu yemek yüksek sodyum içerebilir. Hipertansiyon hastası olarak tüketim miktarına dikkat edin."
    },
    "kidney_disease": {
        "risky_foods": [
            "kuru_fasulye", "kisir", "coban_salata", "beyaz_peynir",
            "sutlac", "mercimek_corbasi", "adana_kebap", "kofte"
        ],
        "message": "Bu yemek böbrek hastalığı olan bireyler için dikkatli tüketilmesi gereken besin öğeleri içerebilir."
    },
    "cholesterol": {
        "risky_foods": [
            "sucuklu_yumurta", "borek", "pogaca", "adana_kebap",
            "baklava", "kunefe", "kofte", "karniyanik", "beyaz_peynir",
            "gozleme"
        ],
        "message": "Bu yemek yüksek doymuş yağ içerebilir. Kolesterol sorununuz olduğu için porsiyon kontrolüne dikkat edin."
    },
    "celiac": {
        "risky_foods": [
            "manti", "lahmacun", "simit", "pogaca", "gozleme", "borek",
            "makarna", "baklava", "kunefe", "tarhana_corbasi",
            "yogurt_corbasi"
        ],
        "message": "Bu yemek glüten içerebilir. Çölyak hastası olarak tüketmekten kaçının."
    },
}


def get_nutrition(food_key: str) -> dict | None:
    """Yemek anahtarına göre besin bilgilerini döndürür."""
    return NUTRITION_DB.get(food_key)


def get_display_name(food_key: str) -> str:
    """Yemek anahtarından Türkçe gösterim adını döndürür."""
    nutrition = NUTRITION_DB.get(food_key)
    if nutrition:
        return nutrition["display_name"]
    return food_key


def build_health_warnings(
    food_key: str,
    is_diabetic: bool = False,
    is_hypertensive: bool = False,
    is_kidney_disease: bool = False,
) -> list[str]:
    """Kullanıcının sağlık profiline göre uyarı listesi oluşturur."""
    warnings = []

    condition_map = {
        "diabetes": is_diabetic,
        "hypertension": is_hypertensive,
        "kidney_disease": is_kidney_disease,
    }

    for condition, has_condition in condition_map.items():
        if not has_condition:
            continue
        disease_info = DISEASE_WARNINGS[condition]
        if food_key in disease_info["risky_foods"]:
            warnings.append(disease_info["message"])

    return warnings
