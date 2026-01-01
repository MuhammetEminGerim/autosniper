from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.api.dependencies import get_current_user, check_rate_limit
from app.models.user import User
from app.models.listing import Listing
from app.services.scraper.arabam_api import ArabamAPIClient
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/quick-search")
async def quick_search(
    current_user: User = Depends(check_rate_limit),
    db: Session = Depends(get_db)
):
    """
    Hızlı tarama - Arabam.com API kullanarak en yeni ilanları çek
    """
    try:
        logger.info(f"Hızlı tarama başlatıldı - Kullanıcı: {current_user.email}")
        
        # API client oluştur
        api_client = ArabamAPIClient()
        
        try:
            # En yeni 20 ilanı çek
            raw_listings = await api_client.get_listings(take=20, skip=0, sort=1)
            
            if not raw_listings:
                logger.warning("API'den ilan gelmedi")
                return {
                    "success": False,
                    "message": "İlan bulunamadı",
                    "count": 0
                }
            
            # İlanları parse et ve database'e kaydet
            saved_count = 0
            for raw_listing in raw_listings:
                try:
                    # Parse et
                    parsed = api_client.parse_listing(raw_listing)
                    
                    if not parsed.get('id'):
                        continue
                    
                    # Database'de var mı kontrol et
                    existing = db.query(Listing).filter(
                        Listing.source_url == parsed['url']
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Yeni ilan oluştur
                    new_listing = Listing(
                        source_url=parsed['url'],
                        title=parsed['title'],
                        price=float(parsed['price']),
                        year=int(parsed['year']),
                        km=int(parsed['km']),
                        location=parsed['location'],
                        date_published=parsed['date'],
                        images=[parsed['photo']] if parsed['photo'] else [],
                        source='arabam_api',
                        is_new=True
                    )
                    
                    db.add(new_listing)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"İlan parse/kayıt hatası: {e}")
                    continue
            
            # Commit
            db.commit()
            
            logger.info(f"Hızlı tarama tamamlandı - {saved_count} yeni ilan kaydedildi")
            
            return {
                "success": True,
                "message": f"{saved_count} yeni ilan bulundu",
                "count": saved_count,
                "total_fetched": len(raw_listings)
            }
            
        finally:
            await api_client.close()
            
    except Exception as e:
        logger.error(f"Hızlı tarama hatası: {e}")
        return {
            "success": False,
            "message": f"Hata: {str(e)}",
            "count": 0
        }
