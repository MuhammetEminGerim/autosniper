from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Admin role
    is_admin = Column(Boolean, default=False, index=True)
    
    # Şifre sıfırlama
    reset_token = Column(String, nullable=True, index=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Telegram bildirimleri
    telegram_chat_id = Column(String, nullable=True)  # Telegram chat ID
    telegram_enabled = Column(Boolean, default=False)
    
    # Subscription/Paket Sistemi
    subscription_tier = Column(String, default="free", index=True)  # free, basic, pro
    daily_search_limit = Column(Integer, default=50)  # Günlük arama limiti
    max_filters = Column(Integer, default=5)  # Maksimum filtre sayısı
    daily_search_count = Column(Integer, default=0)  # Bugünkü arama sayısı
    last_reset_date = Column(Date, default=date.today)  # Son reset tarihi

    # İlişkiler
    filters = relationship("Filter", back_populates="user", cascade="all, delete-orphan")
    listings = relationship("Listing", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    licenses = relationship("License", back_populates="user", cascade="all, delete-orphan")

