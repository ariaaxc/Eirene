from app.core.database import SessionLocal
from app.services.notification_service import check_expiry_and_create_notifications

db = SessionLocal()
count = check_expiry_and_create_notifications(db)
print(f"Создано уведомлений: {count}")
db.close()