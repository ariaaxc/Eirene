from pydantic import BaseModel
from datetime import datetime

class NotificationSettingsUpdate(BaseModel):
    push_enabled: bool = True
    expiry_alerts: bool = True
    telegram_alerts: bool = False

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True