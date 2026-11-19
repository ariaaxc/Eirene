from sqlalchemy.orm import Session
from datetime import date
from app.models.base import UserFridge, Notification, Product
from app.services.fridge_service import get_expiring_product_ids

def check_expiry_and_create_notifications(db: Session):
    """
    Проходит по всем пользователям, ищет у них просрочку и создает алерты.
    """
    # Находим все уникальные ID пользователей, у которых есть холодильник
    user_ids = [r[0] for r in db.query(UserFridge.user_id).distinct().all()]
    
    total_created = 0
    
    for user_id in user_ids:
        # Используем нашу функцию из Этапа 4
        expiring_product_ids = get_expiring_product_ids(user_id, db)
        
        if not expiring_product_ids:
            continue
            
        # Получаем названия продуктов для красивого сообщения
        products = db.query(Product).filter(Product.id.in_(expiring_product_ids)).all()
        product_names = ", ".join([p.name for p in products])
        
        # Проверяем, не создавали ли мы уже такое уведомление сегодня
        existing_alert = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.title == "Внимание! Продукты скоро испортятся"
        ).first()
        
        # Если алерта сегодня не было - создаем
        if not existing_alert:
            new_alert = Notification(
                user_id=user_id,
                title="Внимание! Продукты скоро испортятся",
                message=f"Срок годности истекает у: {product_names}. Скорее приготовьте что-нибудь!"
            )
            db.add(new_alert)
            total_created += 1
            
    db.commit()
    return total_created