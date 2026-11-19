from pydantic import BaseModel
from datetime import date
from typing import Optional
from typing import List, Optional

class ProductShort(BaseModel):
    id: int
    name: str
    category: str
    calories: float
    proteins: float
    fats: float
    carbs: float

    class Config:
        from_attributes = True

class FridgeItemAdd(BaseModel):
    product_id: int
    quantity: float
    added_date: date
    expiration_date: date

class FridgeItemResponse(BaseModel):
    id: int
    quantity: float
    added_date: date
    expiration_date: Optional[date] = None
    product: ProductShort

    class Config:
        from_attributes = True
class AlternativeProduct(BaseModel):
    id: int
    name: str
    calories: float
    health_score: float

class AlternativesResponse(BaseModel):
    original_product: str
    category: str
    alternatives: List[AlternativeProduct]