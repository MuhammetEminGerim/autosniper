from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Fiyat takibi
    price_when_added = Column(Float, nullable=True)  # Favoriye eklendiğindeki fiyat
    price_history = Column(JSON, default=list)  # [{"price": 100000, "date": "2024-01-01"}, ...]
    last_checked_at = Column(DateTime(timezone=True), nullable=True)

    # Her kullanıcı bir ilanı sadece bir kez favoriye ekleyebilir
    __table_args__ = (UniqueConstraint('user_id', 'listing_id', name='unique_user_listing'),)

    user = relationship("User", back_populates="favorites")
    listing = relationship("Listing", back_populates="favorites")

