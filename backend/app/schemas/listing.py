from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DamageInfo(BaseModel):
    """Boya-Değişen ve Tramer bilgisi"""
    original: Optional[List[str]] = []  # Orijinal parçalar
    local_painted: Optional[List[str]] = []  # Lokal boyalı parçalar
    painted: Optional[List[str]] = []  # Boyalı parçalar
    changed: Optional[List[str]] = []  # Değişmiş parçalar
    unknown: Optional[List[str]] = []  # Belirtilmemiş parçalar
    tramer_amount: Optional[str] = None  # Tramer tutarı

class ListingResponse(BaseModel):
    id: int
    source_url: str
    title: str
    price: float
    year: Optional[int]
    brand: Optional[str]
    model: Optional[str]
    fuel_type: Optional[str]
    transmission: Optional[str]
    mileage: Optional[int] = None  # Kilometre
    city: Optional[str]
    description: Optional[str]
    images: Optional[List[str]]
    damage_info: Optional[Dict[str, Any]] = None  # Boya-Değişen bilgisi
    is_new: bool
    scraped_at: datetime

    class Config:
        from_attributes = True

class ListingListResponse(BaseModel):
    items: List[ListingResponse]
    total: int
    page: int
    page_size: int

