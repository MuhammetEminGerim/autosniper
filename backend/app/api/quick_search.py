from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.api.dependencies import get_current_user, check_rate_limit
from app.models.user import User
from app.models.listing import Listing
# from app.services.scraper.arabam_api import ArabamAPIClient # SAHTE API KAPALI
from app.services.scraper.scraper import ArabaComScraper # GERÇEK SCRAPER AÇIK
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
    Hızlı tarama - GERÇEK SİTE (Scraper) kullanarak en yeni ilanları çek
    """
    scraper = None
    try:
        logger.info(f"Gerçek tarama başlatıldı (Scraper Modu) - Kullanıcı: {current_user.email}")

        # Gerçek Scraper'ı başlat
        scraper = ArabaComScraper(db)

        # Tarayıcıyı aç (Scraper.py içinde headless=False yaptık, yani pencere açılacak)
        await scraper.init_browser()

        # İlanları çek
        listings = await scraper.scrape_listings()

        if not listings:
            logger.warning("Siteden ilan çekilemedi (Bot koruması veya boş sonuç)")
            return {
                "success": False,
                "message": "İlan bulunamadı. (Tarayıcı açıldığında müdahale etmeyin)",
                "count": 0
            }

        # İlanları kaydet
        saved_count = await scraper.save_new_listings(listings)

        logger.info(f"Tarama tamamlandı - {saved_count} yeni ilan kaydedildi")

        return {
            "success": True,
            "message": f"{saved_count} yeni ilan bulundu (Gerçek Piyasa Verisi)",
            "count": saved_count,
            "total_fetched": len(listings)
        }

    except Exception as e:
        logger.error(f"Gerçek tarama hatası: {e}")
        return {
            "success": False,
            "message": f"Hata: {str(e)}",
            "count": 0
        }
    finally:
        # İşlem bitince tarayıcıyı kapat
        if scraper:
            await scraper.close_browser()
