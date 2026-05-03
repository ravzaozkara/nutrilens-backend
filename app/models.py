from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Profile fields
    name = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)

    # Health conditions (3 supported per project spec)
    is_diabetic = Column(Boolean, default=False, server_default="false", nullable=False)
    is_hypertensive = Column(Boolean, default=False, server_default="false", nullable=False)
    is_kidney_disease = Column(Boolean, default=False, server_default="false", nullable=False)

    # Daily nutrition goals
    # TODO: compute per-user via Mifflin-St Jeor once height/weight/age/gender are available
    daily_calorie_goal = Column(Float, default=2000, server_default="2000", nullable=False)
    protein_goal = Column(Float, default=90, server_default="90", nullable=False)
    carbs_goal = Column(Float, default=250, server_default="250", nullable=False)
    fat_goal = Column(Float, default=70, server_default="70", nullable=False)

    meals = relationship("Meal", back_populates="user")


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    calories = Column(Integer)
    is_risky_for_diabetic = Column(Boolean, default=False)
    is_risky_for_hypertensive = Column(Boolean, default=False)
    is_risky_for_cholesterol = Column(Boolean, default=False)
    is_risky_for_celiac = Column(Boolean, default=False)
    warning_message = Column(String)


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_label = Column(String, nullable=False)
    calories = Column(Float, default=0)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)
    health_warnings = Column(String, default="")
    image_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, server_default=func.now())

    user = relationship("User", back_populates="meals")
