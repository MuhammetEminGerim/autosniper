from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.dependencies import get_current_user, check_rate_limit, check_filter_limit
from app.models.user import User
from app.models.filter import Filter
from app.models.listing import Listing
from app.schemas.filter import FilterCreate, FilterUpdate, FilterResponse, SchedulerToggle, SchedulerStatus
from app.services.scraper.scraper import ArabaComScraper
import asyncio

router = APIRouter()

@router.get("", response_model=List[FilterResponse])
async def get_filters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filters = db.query(Filter).filter(Filter.user_id == current_user.id).all()
    return filters

@router.post("", response_model=FilterResponse, status_code=status.HTTP_201_CREATED)
async def create_filter(
    filter_data: FilterCreate,
    current_user: User = Depends(check_filter_limit),
    db: Session = Depends(get_db)
):
    next_scan = None
    if filter_data.auto_scan_enabled:
        next_scan = datetime.utcnow() + timedelta(minutes=filter_data.scan_interval)
    
    new_filter = Filter(
        user_id=current_user.id,
        name=filter_data.name,
        criteria=filter_data.criteria,
        is_active=filter_data.is_active,
        auto_scan_enabled=filter_data.auto_scan_enabled,
        scan_interval=filter_data.scan_interval,
        next_scan_at=next_scan
    )
    db.add(new_filter)
    db.commit()
    db.refresh(new_filter)
    return new_filter

@router.put("/{filter_id}", response_model=FilterResponse)
async def update_filter(
    filter_id: int,
    filter_data: FilterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filter_obj = db.query(Filter).filter(
        Filter.id == filter_id,
        Filter.user_id == current_user.id
    ).first()
    
    if not filter_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filtre bulunamadı"
        )
    
    if filter_data.name is not None:
        filter_obj.name = filter_data.name
    if filter_data.criteria is not None:
        filter_obj.criteria = filter_data.criteria
    if filter_data.is_active is not None:
        filter_obj.is_active = filter_data.is_active
    if filter_data.auto_scan_enabled is not None:
        filter_obj.auto_scan_enabled = filter_data.auto_scan_enabled
        if filter_data.auto_scan_enabled:
            filter_obj.next_scan_at = datetime.utcnow() + timedelta(minutes=filter_obj.scan_interval)
    if filter_data.scan_interval is not None:
        filter_obj.scan_interval = filter_data.scan_interval
        if filter_obj.auto_scan_enabled:
            filter_obj.next_scan_at = datetime.utcnow() + timedelta(minutes=filter_data.scan_interval)
    
    db.commit()
    db.refresh(filter_obj)
    return filter_obj

@router.delete("/{filter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_filter(
    filter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filter_obj = db.query(Filter).filter(
        Filter.id == filter_id,
        Filter.user_id == current_user.id
    ).first()
    
    if not filter_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filtre bulunamadı"
        )
    
    db.delete(filter_obj)
    db.commit()
    return None


@router.post("/{filter_id}/search")
async def search_with_filter(
    filter_id: int,
    current_user: User = Depends(check_rate_limit),
    db: Session = Depends(get_db)
):
    """Belirtilen filtreye göre arama yap ve ilanları çek"""
    
    # Filtreyi bul
    filter_obj = db.query(Filter).filter(
        Filter.id == filter_id,
        Filter.user_id == current_user.id
    ).first()
    
    if not filter_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filtre bulunamadı"
        )
    
    # Scraper'ı başlat
    scraper = ArabaComScraper(db)
    
    try:
        await scraper.init_browser()
        
        # Filtre kriterlerine göre arama yap
        listings_data = await scraper.scrape_listings(search_params=filter_obj.criteria)
        
        # İlanları kaydet
        new_count = 0
        for listing_data in listings_data:
            # Aynı URL'li ilan var mı kontrol et
            existing = db.query(Listing).filter(
                Listing.source_url == listing_data["source_url"]
            ).first()
            
            if not existing:
                new_listing = Listing(
                    user_id=current_user.id,
                    filter_id=filter_obj.id,
                    **listing_data
                )
                db.add(new_listing)
                new_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{filter_obj.name} filtresi ile arama tamamlandı",
            "total_found": len(listings_data),
            "new_saved": new_count,
            "filter_criteria": filter_obj.criteria
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Arama sırasında hata: {str(e)}"
        )
    finally:
        await scraper.close_browser()


@router.post("/{filter_id}/scheduler")
async def toggle_scheduler(
    filter_id: int,
    scheduler_data: SchedulerToggle,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Filtrenin otomatik tarama özelliğini aç/kapat"""
    filter_obj = db.query(Filter).filter(
        Filter.id == filter_id,
        Filter.user_id == current_user.id
    ).first()
    
    if not filter_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filtre bulunamadı"
        )
    
    filter_obj.auto_scan_enabled = scheduler_data.enabled
    filter_obj.scan_interval = scheduler_data.interval
    
    if scheduler_data.enabled:
        filter_obj.next_scan_at = datetime.utcnow() + timedelta(minutes=scheduler_data.interval)
    else:
        filter_obj.next_scan_at = None
    
    db.commit()
    db.refresh(filter_obj)
    
    status_text = "aktif" if scheduler_data.enabled else "pasif"
    return {
        "success": True,
        "message": f"Otomatik tarama {status_text} edildi",
        "auto_scan_enabled": filter_obj.auto_scan_enabled,
        "scan_interval": filter_obj.scan_interval,
        "next_scan_at": filter_obj.next_scan_at
    }


@router.get("/scheduler/status", response_model=List[SchedulerStatus])
async def get_scheduler_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tüm filtrelerin scheduler durumunu getir"""
    filters = db.query(Filter).filter(
        Filter.user_id == current_user.id,
        Filter.auto_scan_enabled == True
    ).all()
    
    return [
        SchedulerStatus(
            filter_id=f.id,
            filter_name=f.name,
            auto_scan_enabled=f.auto_scan_enabled,
            scan_interval=f.scan_interval,
            last_scan_at=f.last_scan_at,
            next_scan_at=f.next_scan_at,
            total_scans=f.total_scans or 0,
            new_listings_found=f.new_listings_found or 0
        )
        for f in filters
    ]


@router.get("/scheduler/all-status")
async def get_all_scheduler_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tüm filtrelerin genel istatistiklerini getir"""
    filters = db.query(Filter).filter(Filter.user_id == current_user.id).all()
    
    active_count = sum(1 for f in filters if f.auto_scan_enabled)
    total_scans = sum(f.total_scans or 0 for f in filters)
    total_new = sum(f.new_listings_found or 0 for f in filters)
    
    # En yakın tarama zamanı
    next_scan = None
    for f in filters:
        if f.auto_scan_enabled and f.next_scan_at:
            if next_scan is None or f.next_scan_at < next_scan:
                next_scan = f.next_scan_at
    
    return {
        "total_filters": len(filters),
        "active_schedulers": active_count,
        "total_scans": total_scans,
        "total_new_listings": total_new,
        "next_scan_at": next_scan
    }

