from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from ..database import get_db
from .. import crud, security, schemas, models
from ..dependencies import get_current_user
from ..limiter import limiter

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


def _authenticate_user(db: Session, email: str, password: str) -> models.User:
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı",
        )
    return user


def _build_health_conditions(user: models.User) -> list[str]:
    conditions = []
    if user.is_diabetic:
        conditions.append("diabetes")
    if user.is_hypertensive:
        conditions.append("hypertension")
    if user.is_kidney_disease:
        conditions.append("kidney_disease")
    return conditions


@router.post("/register", response_model=schemas.User)
@limiter.limit("30/minute")
def register(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi zaten kayıtlı."
        )
    return crud.create_user(db, user)


@router.post("/login")
@limiter.limit("30/minute")
def login(request: Request, body: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Frontend JSON login: {email, password} → {access_token, token_type}"""
    user = _authenticate_user(db, body.email, body.password)
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token")
def token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 form login — kept for FastAPI /docs Authorize button."""
    user = _authenticate_user(db, form_data.username, form_data.password)
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Oturum açık kullanıcının tam profilini döndürür."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "birth_date": current_user.birth_date,
        "gender": current_user.gender,
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "is_diabetic": current_user.is_diabetic,
        "is_hypertensive": current_user.is_hypertensive,
        "is_kidney_disease": current_user.is_kidney_disease,
        "daily_calorie_goal": current_user.daily_calorie_goal,
        "protein_goal": current_user.protein_goal,
        "carbs_goal": current_user.carbs_goal,
        "fat_goal": current_user.fat_goal,
        "health_conditions": _build_health_conditions(current_user),
    }


@router.put("/profile")
def update_profile(
    body: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Kullanıcı profilini kısmen günceller."""
    updated = crud.update_user(db, current_user, body)
    return {
        "id": updated.id,
        "email": updated.email,
        "name": updated.name,
        "birth_date": updated.birth_date,
        "gender": updated.gender,
        "height_cm": updated.height_cm,
        "weight_kg": updated.weight_kg,
        "is_diabetic": updated.is_diabetic,
        "is_hypertensive": updated.is_hypertensive,
        "is_kidney_disease": updated.is_kidney_disease,
        "daily_calorie_goal": updated.daily_calorie_goal,
        "protein_goal": updated.protein_goal,
        "carbs_goal": updated.carbs_goal,
        "fat_goal": updated.fat_goal,
        "health_conditions": _build_health_conditions(updated),
    }


@router.put("/password")
def change_password(
    body: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Şifre değiştirme: mevcut şifreyi doğrular, yeni hash'i kaydeder."""
    if not security.verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mevcut şifre hatalı.",
        )
    current_user.hashed_password = security.get_password_hash(body.new_password)
    db.commit()
    return {"success": True, "message": "Şifre başarıyla güncellendi."}
