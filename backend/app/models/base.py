from sqlalchemy import Column, Integer, Float, Date, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from datetime import date
from app.core.database import Base
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    category = Column(String(255))
    calories = Column(Float)
    proteins = Column(Float)
    fats = Column(Float)
    carbs = Column(Float)
    shelf_life_days = Column(Integer)
    health_score = Column(Float)

class UserFridge(Base):
    __tablename__ = "user_fridge"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[float]
    added_date: Mapped[Optional[date]]
    expiration_date: Mapped[Optional[date]]
    price: Mapped[Optional[float]]
    
    product: Mapped["Product"] = relationship("Product")

class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float)
    store_name = Column(String(255))
    purchased_at = Column(Date)

class ReceiptItem(Base):
    __tablename__ = "receipt_items"
    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float)
    price = Column(Float)

class NotificationSettings(Base):
    __tablename__ = "notification_settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    push_enabled = Column(Boolean, default=True)
    expiry_alerts = Column(Boolean, default=True)
    telegram_alerts = Column(Boolean, default=False)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    message = Column(String(1000), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())