from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.base import UserFridge

def get_expiring_product_ids(user_id: int, db: Session) -> list[int]:
    """
    Возвращает список ID продуктов, которые испортятся в ближайшие 48 часов.
    Настя Г. будет использовать это в алгоритме рецептов.
    """
    warning_date = date.today() + timedelta(days=2)
    
    # Достаем записи из холодильника
    expiring_items = db.query(UserFridge).filter(
        UserFridge.user_id == user_id,
        UserFridge.expiration_date <= warning_date,
        UserFridge.expiration_date >= date.today() # Не берем уже просроченные
    ).all()
    
    # Возвращаем только ID продуктов
    return [item.product_id for item in expiring_items]