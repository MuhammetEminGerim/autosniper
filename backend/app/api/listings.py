from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.listing import Listing
from app.schemas.listing import ListingResponse, ListingListResponse

router = APIRouter()

@router.get("", response_model=ListingListResponse)
async def get_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    brand: Optional[str] = None,
    city: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_new: Optional[bool] = None,
    source: Optional[str] = Query(None, description="all, quick, filtered"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Listing)
    
    # Kaynak filtreleme (hızlı tarama vs özel filtre)
    if source == "quick":
        query = query.filter(Listing.filter_id == None)
    elif source == "filtered":
        query = query.filter(Listing.filter_id != None)
    # source == "all" veya None ise filtre yok, hepsini getir
    
    # Filtreleme
    if brand:
        query = query.filter(Listing.brand.ilike(f"%{brand}%"))
    if city:
        query = query.filter(Listing.city.ilike(f"%{city}%"))
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if is_new is not None:
        query = query.filter(Listing.is_new == is_new)
    
    # Toplam sayı
    total = query.count()
    
    # Sayfalama
    items = query.order_by(Listing.scraped_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return ListingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/statistics")
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Piyasa istatistiklerini getir"""
    
    # Temel istatistikler
    total_listings = db.query(func.count(Listing.id)).scalar() or 0
    avg_price = db.query(func.avg(Listing.price)).scalar() or 0
    min_price = db.query(func.min(Listing.price)).scalar() or 0
    max_price = db.query(func.max(Listing.price)).scalar() or 0
    avg_mileage = db.query(func.avg(Listing.mileage)).filter(Listing.mileage != None).scalar() or 0
    avg_year = db.query(func.avg(Listing.year)).filter(Listing.year != None).scalar() or 0
    
    # Son 24 saatte eklenen ilanlar
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_listings_24h = db.query(func.count(Listing.id)).filter(
        Listing.scraped_at >= yesterday
    ).scalar() or 0
    
    # 7 günlük fiyat değişimi (basit hesaplama)
    week_ago = datetime.utcnow() - timedelta(days=7)
    old_avg = db.query(func.avg(Listing.price)).filter(
        Listing.scraped_at < week_ago
    ).scalar() or avg_price
    
    if old_avg and old_avg > 0:
        price_change_7d = ((avg_price - old_avg) / old_avg) * 100
    else:
        price_change_7d = 0
    
    # Marka dağılımı
    brand_stats = []
    if total_listings > 0:
        brands = db.query(
            Listing.brand,
            func.count(Listing.id).label('count'),
            func.avg(Listing.price).label('avg_price')
        ).filter(Listing.brand != None).group_by(Listing.brand).order_by(
            func.count(Listing.id).desc()
        ).limit(15).all()
        
        for brand in brands:
            if brand.brand:
                brand_stats.append({
                    "brand": brand.brand,
                    "count": brand.count,
                    "avg_price": float(brand.avg_price or 0),
                    "percentage": (brand.count / total_listings) * 100
                })
    
    # Şehir dağılımı
    city_stats = []
    if total_listings > 0:
        cities = db.query(
            Listing.city,
            func.count(Listing.id).label('count'),
            func.avg(Listing.price).label('avg_price')
        ).filter(Listing.city != None).group_by(Listing.city).order_by(
            func.count(Listing.id).desc()
        ).limit(15).all()
        
        for city in cities:
            if city.city:
                city_stats.append({
                    "city": city.city,
                    "count": city.count,
                    "avg_price": float(city.avg_price or 0),
                    "percentage": (city.count / total_listings) * 100
                })
    
    # Fiyat aralıkları
    price_ranges = []
    ranges = [
        (0, 500000, "0-500K"),
        (500000, 1000000, "500K-1M"),
        (1000000, 1500000, "1M-1.5M"),
        (1500000, 2000000, "1.5M-2M"),
        (2000000, 3000000, "2M-3M"),
        (3000000, 5000000, "3M-5M"),
        (5000000, float('inf'), "5M+")
    ]
    
    for min_p, max_p, label in ranges:
        if max_p == float('inf'):
            count = db.query(func.count(Listing.id)).filter(
                Listing.price >= min_p
            ).scalar() or 0
        else:
            count = db.query(func.count(Listing.id)).filter(
                Listing.price >= min_p,
                Listing.price < max_p
            ).scalar() or 0
        
        percentage = (count / total_listings * 100) if total_listings > 0 else 0
        price_ranges.append({
            "range": label,
            "count": count,
            "percentage": percentage
        })
    
    return {
        "market": {
            "total_listings": total_listings,
            "avg_price": float(avg_price),
            "min_price": float(min_price),
            "max_price": float(max_price),
            "avg_mileage": float(avg_mileage),
            "avg_year": float(avg_year),
            "price_change_7d": float(price_change_7d),
            "new_listings_24h": new_listings_24h
        },
        "brands": brand_stats,
        "cities": city_stats,
        "price_ranges": price_ranges
    }


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="İlan bulunamadı"
        )
    return listing


@router.delete("/{listing_id}")
async def delete_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tek bir ilanı sil"""
    from fastapi import HTTPException, status
    from app.models.favorite import Favorite
    
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="İlan bulunamadı"
        )
    
    # Önce bu ilana ait favorileri sil
    db.query(Favorite).filter(Favorite.listing_id == listing_id).delete()
    
    db.delete(listing)
    db.commit()
    
    return {"message": "İlan başarıyla silindi", "id": listing_id}


@router.delete("")
async def delete_all_listings(
    source: Optional[str] = Query(None, description="all, quick, filtered - hangi kaynaktan silinecek"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kaynağa göre ilanları sil"""
    from app.models.favorite import Favorite
    
    # Silinecek ilanları belirle
    listing_query = db.query(Listing)
    
    if source == "quick":
        # Sadece hızlı tarama (filter_id = None)
        listing_query = listing_query.filter(Listing.filter_id == None)
    elif source == "filtered":
        # Sadece filtrelerden gelen (filter_id != None)
        listing_query = listing_query.filter(Listing.filter_id != None)
    # source == "all" veya None ise hepsini sil
    
    # Silinecek ilan ID'lerini al
    listing_ids = [l.id for l in listing_query.all()]
    
    if listing_ids:
        # Bu ilanlara ait favorileri sil
        db.query(Favorite).filter(Favorite.listing_id.in_(listing_ids)).delete(synchronize_session=False)
        
        # İlanları sil
        count = listing_query.delete(synchronize_session=False)
        db.commit()
    else:
        count = 0
    
    return {"message": f"{count} ilan silindi", "count": count}

