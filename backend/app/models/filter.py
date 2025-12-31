from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Filter(Base):
    __tablename__ = "filters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    criteria = Column(JSON, nullable=False)  # Filtre kriterleri (marka, model, yıl, fiyat vb.)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Otomatik tarama alanları
    auto_scan_enabled = Column(Boolean, default=False)
    scan_interval = Column(Integer, default=30)  # Dakika cinsinden (15, 30, 60, 120, 360, 720, 1440)
    last_scan_at = Column(DateTime(timezone=True), nullable=True)
    next_scan_at = Column(DateTime(timezone=True), nullable=True)
    total_scans = Column(Integer, default=0)
    new_listings_found = Column(Integer, default=0)

    # İlişkiler
    user = relationship("User", back_populates="filters")
    listings = relationship("Listing", back_populates="filter")
    notifications = relationship("Notification", back_populates="filter")

