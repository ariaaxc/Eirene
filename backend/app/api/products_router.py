from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.base import Product
from app.schemas.fridge import ProductShort, AlternativesResponse
from app.core.database import get_db

router = APIRouter(prefix="/api/products", tags=["Справочник продуктов"])

# 1. Поиск продуктов (автокомплит)
@router.get("/", response_model=List[ProductShort])
def search_products(
    query: str = Query("", description="Поиск по названию для автокомплита"),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    products = db.query(Product).filter(Product.name.ilike(f"%{query}%")).limit(limit).all()
    return products

# 2. Поиск полезных альтернатив (Task 4.4)
@router.get("/{product_id}/alternatives", response_model=AlternativesResponse)
def get_healthy_alternatives(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    
    alternatives = db.query(Product).filter(
        Product.category == product.category,
        Product.id != product.id,
        (Product.calories < product.calories) | (Product.health_score > product.health_score)
    ).order_by(Product.calories.asc()).limit(5).all()
    
    return {
        "original_product": product.name,
        "category": product.category,
        "alternatives": alternatives
    }