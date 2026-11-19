from datetime import datetime, date
from pydantic import BaseModel


# --- РЕЦЕПТЫ ---

class RecipeIngredientOut(BaseModel):
    product_id: int
    quantity: float


class RecipeOut(BaseModel):
    id: int
    name: str
    instructions: str
    calories: float | None = None
    ingredients: list[RecipeIngredientOut] = []


class WhatToCookOut(BaseModel):
    id: int
    name: str
    instructions: str
    calories: float | None = None
    total_ingredients: int
    available_ingredients: int


# --- ДНЕВНИК ПИТАНИЯ ---

class MealLogCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: float
    meal_type: str  # breakfast, lunch, dinner, snack


class MealLogOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: float
    meal_type: str
    eaten_at: datetime
    total_calories: float = 0.0
    total_proteins: float = 0.0
    total_fats: float = 0.0
    total_carbs: float = 0.0


# --- ЧЕКИ И ПОКУПКИ ---

class ReceiptItemOut(BaseModel):
    id: int
    product_id: int | None = None
    raw_name: str
    quantity: float
    price: float


class ReceiptOut(BaseModel):
    id: int
    user_id: int
    total_amount: float
    store_name: str | None = None
    purchased_at: datetime
    items: list[ReceiptItemOut] = []


# --- РАЦИОН И КБЖУ ---

class RationTargetCreate(BaseModel):
    user_id: int
    target_calories: float
    target_proteins: float
    target_fats: float
    target_carbs: float


class RationItemOut(BaseModel):
    product_id: int
    name: str
    grams: float
    calories: float
    proteins: float
    fats: float
    carbs: float

class RationOut(BaseModel):
    target_calories: float
    eaten_today: float
    remaining_deficit: float
    ration_calories: float
    recipes: list[str]


# --- РЕЦЕПТЫ И ПРИОРИТЕТ ПО СРОКУ ГОДНОСТИ ---

class WhatToCookOut(BaseModel):
    id: int
    name: str
    instructions: str
    calories: float | None = None
    total_ingredients: int
    available_ingredients: int
    earliest_expiration: date | None = None
