from datetime import date, datetime, time, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from .. import models, schemas, crud
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/meals",
    tags=["meals"]
)


@router.post("/", response_model=schemas.MealResponse)
def create_meal(
    meal_data: schemas.MealCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Yeni bir öğün kaydı oluşturur."""
    return crud.create_meal(db, user.id, meal_data)


@router.get("/", response_model=list[schemas.MealResponse])
def list_meals(
    filter_date: Optional[date] = Query(None, description="Belirli bir tarihe göre filtrele (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Kullanıcının öğün geçmişini listeler."""
    if filter_date:
        start = datetime.combine(filter_date, time.min)
        end = datetime.combine(filter_date, time.max)
        return (
            db.query(models.Meal)
            .filter(
                models.Meal.user_id == user.id,
                models.Meal.created_at >= start,
                models.Meal.created_at <= end,
            )
            .order_by(models.Meal.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    return crud.get_meals_by_user(db, user.id, skip=skip, limit=limit)


@router.get("/summary", response_model=schemas.MealSummary)
def meal_summary(
    summary_date: Optional[date] = Query(None, description="Özet tarihi (varsayılan: bugün)"),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Günlük kalori ve makro besin özeti."""
    target_date = summary_date or date.today()
    start = datetime.combine(target_date, time.min)
    end = datetime.combine(target_date, time.max)

    meals = (
        db.query(models.Meal)
        .filter(
            models.Meal.user_id == user.id,
            models.Meal.created_at >= start,
            models.Meal.created_at <= end,
        )
        .all()
    )

    return {
        "total_calories": sum(m.calories for m in meals),
        "total_protein": sum(m.protein for m in meals),
        "total_carbs": sum(m.carbs for m in meals),
        "total_fat": sum(m.fat for m in meals),
        "meal_count": len(meals),
    }


@router.get("/weekly-summary", response_model=list[schemas.WeeklyDaySummary])
def weekly_summary(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Son 7 günün günlük kalori/makro özetini döndürür (sıfır günleri de dahil)."""
    today = date.today()
    result = []
    for offset in range(6, -1, -1):
        target_date = today - timedelta(days=offset)
        start = datetime.combine(target_date, time.min)
        end = datetime.combine(target_date, time.max)
        meals = (
            db.query(models.Meal)
            .filter(
                models.Meal.user_id == user.id,
                models.Meal.created_at >= start,
                models.Meal.created_at <= end,
            )
            .all()
        )
        result.append({
            "date": target_date,
            "total_calories": sum(m.calories for m in meals),
            "total_protein": sum(m.protein for m in meals),
            "total_carbs": sum(m.carbs for m in meals),
            "total_fat": sum(m.fat for m in meals),
            "meal_count": len(meals),
        })
    return result


@router.delete("/{meal_id}")
def delete_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Kullanıcının kendi öğün kaydını siler."""
    meal = crud.get_meal(db, meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Öğün bulunamadı.")
    if meal.user_id != user.id:
        raise HTTPException(status_code=403, detail="Bu öğünü silme yetkiniz yok.")

    crud.delete_meal(db, meal_id)
    return {"message": "Öğün başarıyla silindi."}
