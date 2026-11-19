from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, timedelta
from app.models.base import UserFridge, Product
from app.schemas.fridge import FridgeItemAdd, FridgeItemResponse
from app.core.database import get_db

router = APIRouter(prefix="/api/fridge", tags=["Холодильник"])

@router.get("/{user_id}", response_model=List[FridgeItemResponse])
def get_user_fridge(user_id: int, db: Session = Depends(get_db)):
    return db.query(UserFridge).filter(UserFridge.user_id == user_id).all()

@router.post("/", response_model=FridgeItemResponse)
def add_to_fridge(user_id: int, item: FridgeItemAdd, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден в базе")
    
    new_item = UserFridge(
        user_id=user_id,
        product_id=item.product_id,
        quantity=item.quantity,
        added_date=item.added_date,
        expiration_date=item.expiration_date
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.delete("/{id}")
def delete_from_fridge(id: int, db: Session = Depends(get_db)):
    item = db.query(UserFridge).filter(UserFridge.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    db.delete(item)
    db.commit()
    return {"message": "Продукт удален из холодильника"}

@router.get("/{user_id}/volume")
def get_fridge_volume(user_id: int, db: Session = Depends(get_db)):
    TOTAL_LIMIT = 10000.0
    
    total_weight = db.query(func.sum(UserFridge.quantity)).filter(UserFridge.user_id == user_id).scalar()
    total_weight = total_weight if total_weight else 0.0
    
    percentage = min(round((total_weight / TOTAL_LIMIT) * 100, 2), 100.0)
    
    return {"total_weight": total_weight, "fill_percentage": percentage}

@router.get("/{user_id}/expiring", response_model=List[FridgeItemResponse])
def get_expiring_products(user_id: int, db: Session = Depends(get_db)):
    warning_date = date.today() + timedelta(days=2)
    return db.query(UserFridge).filter(
        UserFridge.user_id == user_id,
        UserFridge.expiration_date <= warning_date
    ).all()