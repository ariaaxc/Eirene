from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.base import Notification, NotificationSettings
from app.schemas.notifications import NotificationSettingsUpdate, NotificationResponse

router = APIRouter(prefix="/api/notifications", tags=["Уведомления"])

# 1. Сохранение настроек пушей
@router.post("/settings/{user_id}")
def save_settings(user_id: int, settings: NotificationSettingsUpdate, db: Session = Depends(get_db)):
    # Проверяем, есть ли уже настройки у юзера
    db_settings = db.query(NotificationSettings).filter(NotificationSettings.user_id == user_id).first()
    
    if db_settings:
        # Если есть - обновляем
        db_settings.push_enabled = settings.push_enabled
        db_settings.expiry_alerts = settings.expiry_alerts
        db_settings.telegram_alerts = settings.telegram_alerts
    else:
        # Если нет - создаем
        db_settings = NotificationSettings(
            user_id=user_id,
            push_enabled=settings.push_enabled,
            expiry_alerts=settings.expiry_alerts,
            telegram_alerts=settings.telegram_alerts
        )
        db.add(db_settings)
        
    db.commit()
    return {"status": "success", "message": "Настройки сохранены"}

# 2. История накопившихся алертов
@router.get("/{user_id}", response_model=List[NotificationResponse])
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()
    return notifications