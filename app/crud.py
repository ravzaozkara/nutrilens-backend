from sqlalchemy.orm import Session
from . import models, schemas, security


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        birth_date=user.birth_date,
        gender=user.gender,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        is_diabetic=user.is_diabetic,
        is_hypertensive=user.is_hypertensive,
        is_kidney_disease=user.is_kidney_disease,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def update_user(db: Session, user: models.User, data: schemas.UserUpdate):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def create_meal(db: Session, user_id: int, meal_data: schemas.MealCreate):
    db_meal = models.Meal(
        user_id=user_id,
        food_label=meal_data.food_label,
        calories=meal_data.calories,
        protein=meal_data.protein,
        carbs=meal_data.carbs,
        fat=meal_data.fat,
        health_warnings=meal_data.health_warnings,
        image_path=meal_data.image_path,
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


def get_meals_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    return (
        db.query(models.Meal)
        .filter(models.Meal.user_id == user_id)
        .order_by(models.Meal.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_meal(db: Session, meal_id: int):
    return db.query(models.Meal).filter(models.Meal.id == meal_id).first()


def delete_meal(db: Session, meal_id: int):
    meal = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if meal:
        db.delete(meal)
        db.commit()
    return meal
