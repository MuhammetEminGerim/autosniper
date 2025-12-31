from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.listing import Listing
from app.models.favorite import Favorite

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


class FavoriteResponse(BaseModel):
    id: int
    listing_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PriceChange(BaseModel):
    original_price: Optional[float] = None
    current_price: float
    difference: float = 0
    percentage: float = 0
    direction: str = "same"  # "up", "down", "same"


class ListingResponse(BaseModel):
    id: int
    title: str
    price: float
    year: int | None
    brand: str | None
    city: str | None
    fuel_type: str | None
    transmission: str | None
    images: list | None
    source_url: str
    is_favorite: bool = True
    price_change: Optional[PriceChange] = None
    price_history: Optional[list] = None

    class Config:
        from_attributes = True


def calculate_price_change(original_price: float, current_price: float) -> PriceChange:
    """Fiyat değişimini hesapla"""
    if not original_price or original_price == 0:
        return PriceChange(
            original_price=None,
            current_price=current_price,
            difference=0,
            percentage=0,
            direction="same"
        )
    
    difference = current_price - original_price
    percentage = ((current_price - original_price) / original_price) * 100
    
    if difference > 0:
        direction = "up"
    elif difference < 0:
        direction = "down"
    else:
        direction = "same"
    
    return PriceChange(
        original_price=original_price,
        current_price=current_price,
        difference=difference,
        percentage=round(percentage, 1),
        direction=direction
    )


@router.get("", response_model=List[ListingResponse])
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının favori ilanlarını getir (fiyat değişimleriyle)"""
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    
    listings = []
    for fav in favorites:
        listing = db.query(Listing).filter(Listing.id == fav.listing_id).first()
        if listing:
            # Fiyat değişimini hesapla
            price_change = None
            if fav.price_when_added:
                price_change = calculate_price_change(fav.price_when_added, listing.price)
            
            listing_dict = {
                "id": listing.id,
                "title": listing.title,
                "price": listing.price,
                "year": listing.year,
                "brand": listing.brand,
                "city": listing.city,
                "fuel_type": listing.fuel_type,
                "transmission": listing.transmission,
                "images": listing.images,
                "source_url": listing.source_url,
                "is_favorite": True,
                "price_change": price_change,
                "price_history": fav.price_history or []
            }
            listings.append(listing_dict)
    
    return listings


@router.post("/{listing_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """İlanı favorilere ekle (fiyat kaydedilir)"""
    # İlan var mı kontrol et
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="İlan bulunamadı"
        )
    
    # Zaten favoride mi kontrol et
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.listing_id == listing_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu ilan zaten favorilerinizde"
        )
    
    # Favoriye ekle - fiyatı kaydet
    favorite = Favorite(
        user_id=current_user.id, 
        listing_id=listing_id,
        price_when_added=listing.price,
        price_history=[{
            "price": listing.price,
            "date": datetime.utcnow().isoformat()
        }],
        last_checked_at=datetime.utcnow()
    )
    db.add(favorite)
    db.commit()
    
    return {
        "message": "İlan favorilere eklendi", 
        "listing_id": listing_id,
        "price_tracked": listing.price
    }


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """İlanı favorilerden çıkar"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.listing_id == listing_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu ilan favorilerinizde değil"
        )
    
    db.delete(favorite)
    db.commit()
    
    return None


@router.get("/check/{listing_id}")
async def check_favorite(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """İlanın favoride olup olmadığını kontrol et"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.listing_id == listing_id
    ).first()
    
    return {"is_favorite": favorite is not None}

