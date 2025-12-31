from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Float, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Hangi kullanıcı için çekildi
    filter_id = Column(Integer, ForeignKey("filters.id"), nullable=True)  # Hangi filtre ile çekildi
    source_url = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False, index=True)  # Fiyat sıralaması için index
    year = Column(Integer, index=True)  # Yıl filtreleme için index
    brand = Column(String, index=True)
    model = Column(String, index=True)
    fuel_type = Column(String, index=True)  # Yakıt tipi filtreleme için
    transmission = Column(String, index=True)  # Vites filtreleme için
    mileage = Column(Integer, nullable=True, index=True)  # Kilometre filtreleme için
    city = Column(String, index=True)
    description = Column(String)
    images = Column(JSON)  # Resim URL'leri listesi
    
    # Boya-Değişen ve Tramer bilgisi
    damage_info = Column(JSON, nullable=True)  # {"original": [...], "painted": [...], "changed": [...], "tramer_amount": "..."}
    
    is_new = Column(Boolean, default=True, index=True)  # Yeni ilan filtresi için
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # Tarih sıralaması için
    
    # Composite indeksler - sık kullanılan sorgu kombinasyonları için
    __table_args__ = (
        Index('idx_listings_brand_price', 'brand', 'price'),  # Marka + fiyat araması
        Index('idx_listings_city_price', 'city', 'price'),    # Şehir + fiyat araması
        Index('idx_listings_filter_id_scraped', 'filter_id', 'scraped_at'),  # Filtre ilanları
        Index('idx_listings_scraped_at_desc', scraped_at.desc()),  # En yeni ilanlar
    )

    # İlişkiler
    user = relationship("User", back_populates="listings")
    filter = relationship("Filter", back_populates="listings")
    notifications = relationship("Notification", back_populates="listing")
    favorites = relationship("Favorite", back_populates="listing", cascade="all, delete-orphan")

