from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime, date


# ── Auth / User ────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    is_diabetic: bool = False
    is_hypertensive: bool = False
    is_kidney_disease: bool = False

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        if v < date(1900, 1, 1):
            raise ValueError("Doğum tarihi 1900-01-01 tarihinden önce olamaz.")
        if v > date.today():
            raise ValueError("Doğum tarihi bugünden sonra olamaz.")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    is_diabetic: Optional[bool] = None
    is_hypertensive: Optional[bool] = None
    is_kidney_disease: Optional[bool] = None
    daily_calorie_goal: Optional[float] = None
    protein_goal: Optional[float] = None
    carbs_goal: Optional[float] = None
    fat_goal: Optional[float] = None

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        if v < date(1900, 1, 1):
            raise ValueError("Doğum tarihi 1900-01-01 tarihinden önce olamaz.")
        if v > date.today():
            raise ValueError("Doğum tarihi bugünden sonra olamaz.")
        return v


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    is_diabetic: bool
    is_hypertensive: bool
    is_kidney_disease: bool
    daily_calorie_goal: float
    protein_goal: float
    carbs_goal: float
    fat_goal: float


# ── Food ───────────────────────────────────────────────────────────────────────

class FoodBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    calories: int
    is_risky_for_diabetic: bool
    is_risky_for_hypertensive: bool
    is_risky_for_cholesterol: bool
    is_risky_for_celiac: bool
    warning_message: str


# ── Analysis ───────────────────────────────────────────────────────────────────

class AnalysisResult(BaseModel):
    food_name: str
    confidence: float
    health_warning: str
    calories: float
    protein: float = 0
    carbs: float = 0
    fat: float = 0


class ImageAnalysisResult(BaseModel):
    food_name: str
    confidence: float
    health_warning: str
    calories: float
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    image_path: str


# ── Meals ──────────────────────────────────────────────────────────────────────

class MealCreate(BaseModel):
    food_label: str
    calories: float = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    health_warnings: str = ""
    image_path: Optional[str] = None


class MealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    food_label: str
    calories: float
    protein: float
    carbs: float
    fat: float
    health_warnings: str
    image_path: Optional[str]
    created_at: datetime


class MealSummary(BaseModel):
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    meal_count: int


class WeeklyDaySummary(BaseModel):
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    meal_count: int
