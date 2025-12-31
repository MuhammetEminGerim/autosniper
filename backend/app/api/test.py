from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.api.dependencies import get_current_user, check_rate_limit
from app.models.user import User
from app.models.listing import Listing
from app.models.filter import Filter
from app.services.filter_matcher import FilterMatcher
from app.services.websocket.manager import manager
from app.services.scraper.scraper import ArabaComScraper
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/test/add-listing")
async def add_test_listing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test için örnek ilan ekle ve filtreleri kontrol et
    """
    # Test ilanı oluştur
    test_listing = Listing(
        source_url=f"https://test-araba.com/ilan-{datetime.now().timestamp()}",
        title="Test Araç - Audi A3 2018 Dizel Otomatik",
        price=850000.0,
        year=2018,
        brand="Audi",
        model="A3",
        fuel_type="dizel",
        transmission="otomatik",
        city="Ankara",
        description="Test için eklenen örnek ilan. Bu ilan filtrelerinize uyuyorsa bildirim alacaksınız.",
        images=["https://via.placeholder.com/600x400?text=Test+Araç"],
        is_new=True
    )
    
    db.add(test_listing)
    db.flush()  # ID'yi almak için
    
    # Kullanıcının aktif filtrelerini al
    user_filters = db.query(Filter).filter(
        Filter.user_id == current_user.id,
        Filter.is_active == True
    ).all()
    
    matching_filters = []
    
    # Filtreleri kontrol et
    for filter_obj in user_filters:
        if FilterMatcher.matches(test_listing, filter_obj):
            matching_filters.append(filter_obj)
            
            # WebSocket bildirimi gönder
            try:
                await manager.send_personal_message({
                    "type": "new_listing",
                    "message": f"🎯 Filtrenize uyan yeni ilan bulundu: {test_listing.title}",
                    "listing": {
                        "id": test_listing.id,
                        "title": test_listing.title,
                        "price": test_listing.price,
                        "source_url": test_listing.source_url,
                        "year": test_listing.year,
                        "brand": test_listing.brand,
                        "model": test_listing.model,
                        "city": test_listing.city,
                    },
                    "filter_id": filter_obj.id,
                    "filter_name": filter_obj.name,
                }, current_user.id)
                
                logger.info(f"Test ilanı için bildirim gönderildi: Filtre {filter_obj.name}")
            except Exception as e:
                logger.error(f"Bildirim gönderilirken hata: {e}")
    
    db.commit()
    
    return {
        "message": "Test ilanı eklendi",
        "listing": {
            "id": test_listing.id,
            "title": test_listing.title,
            "price": test_listing.price,
            "year": test_listing.year,
            "brand": test_listing.brand,
            "model": test_listing.model,
            "city": test_listing.city,
        },
        "total_filters": len(user_filters),
        "matching_filters": [
            {
                "id": f.id,
                "name": f.name,
                "criteria": f.criteria
            } for f in matching_filters
        ],
        "notification_sent": len(matching_filters) > 0
    }

@router.post("/test/add-custom-listing")
async def add_custom_test_listing(
    title: str = "Test Araç",
    price: float = 500000.0,
    year: int = 2020,
    brand: str = "Audi",
    model: str = "A3",
    fuel_type: str = "dizel",
    transmission: str = "otomatik",
    city: str = "Ankara",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Özelleştirilmiş test ilanı ekle
    """
    test_listing = Listing(
        source_url=f"https://test-araba.com/ilan-{datetime.now().timestamp()}",
        title=title,
        price=price,
        year=year,
        brand=brand,
        model=model,
        fuel_type=fuel_type,
        transmission=transmission,
        city=city,
        description="Test için eklenen örnek ilan.",
        images=["https://via.placeholder.com/600x400?text=Test+Araç"],
        is_new=True
    )
    
    db.add(test_listing)
    db.flush()
    
    # Filtreleri kontrol et
    user_filters = db.query(Filter).filter(
        Filter.user_id == current_user.id,
        Filter.is_active == True
    ).all()
    
    matching_filters = []
    for filter_obj in user_filters:
        if FilterMatcher.matches(test_listing, filter_obj):
            matching_filters.append(filter_obj)
            try:
                await manager.send_personal_message({
                    "type": "new_listing",
                    "message": f"🎯 Test ilanı: {test_listing.title}",
                    "listing": {
                        "id": test_listing.id,
                        "title": test_listing.title,
                        "price": test_listing.price,
                        "source_url": test_listing.source_url,
                    },
                    "filter_id": filter_obj.id,
                    "filter_name": filter_obj.name,
                }, current_user.id)
            except Exception as e:
                logger.error(f"Bildirim hatası: {e}")
    
    db.commit()
    
    return {
        "message": "Özel test ilanı eklendi",
        "listing_id": test_listing.id,
        "matches_filters": len(matching_filters),
        "matching_filter_names": [f.name for f in matching_filters]
    }

@router.post("/scrape")
async def scrape_with_criteria(
    criteria: dict = {},
    current_user: User = Depends(check_rate_limit),
    db: Session = Depends(get_db)
):
    """
    Kriterlere göre gerçek siteden ilanları çek (Arama sayfası için)
    """
    import sys
    print("=" * 50, file=sys.stderr)
    print("ARAMA BAŞLADI", file=sys.stderr)
    print(f"Kriterler: {criteria}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    scraper = None
    try:
        scraper = ArabaComScraper(db)
        await scraper.init_browser()
        
        # Kriterleri scraper'a gönder
        search_params = criteria.get("criteria", criteria) if criteria else {}
        listings = await scraper.scrape_listings(search_params)
        
        new_count = await scraper.save_new_listings(listings)
        
        await scraper.close_browser()
        
        return {
            "message": "Arama tamamlandı",
            "total_scraped": len(listings),
            "new_listings_added": new_count
        }
    except Exception as e:
        print(f"HATA: {e}", file=sys.stderr)
        if scraper:
            try:
                await scraper.close_browser()
            except:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Arama başarısız: {str(e)}"
        )


@router.post("/scrape-real-listings")
async def scrape_real_listings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gerçek siteden ilanları çek ve sisteme ekle (TEST İÇİN - eski endpoint)
    """
    import sys
    print("=" * 50, file=sys.stderr)
    print("SCRAPER TEST BAŞLADI", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    scraper = None
    try:
        print("1. Scraper başlatılıyor...", file=sys.stderr)
        logger.info("=" * 50)
        logger.info("SCRAPER TEST BAŞLADI")
        logger.info("=" * 50)
        logger.info("Scraper başlatılıyor...")
        
        # Scraper'ı başlat
        scraper = ArabaComScraper(db)
        print("2. Tarayıcı başlatılıyor...", file=sys.stderr)
        logger.info("Tarayıcı başlatılıyor...")
        await scraper.init_browser()
        print("3. Tarayıcı başlatıldı!", file=sys.stderr)
        logger.info("Tarayıcı başlatıldı")
        
        # İlanları çek (örnek parametrelerle)
        print("4. İlanlar çekiliyor...", file=sys.stderr)
        logger.info("İlanlar çekiliyor...")
        listings = await scraper.scrape_listings({
            "brand": None,  # Tüm markalar
            "city": None    # Tüm şehirler
        })
        print(f"5. Toplam {len(listings)} ilan bulundu", file=sys.stderr)
        logger.info(f"Toplam {len(listings)} ilan bulundu")
        
        # Bulunan ilanları logla
        for i, listing in enumerate(listings[:5]):
            print(f"   İlan {i+1}: {listing.get('title', 'N/A')[:50]} - {listing.get('price', 0)} TL", file=sys.stderr)
            logger.info(f"İlan {i+1}: {listing.get('title', 'N/A')} - {listing.get('price', 0)} TL")
        
        # Yeni ilanları kaydet ve filtreleri kontrol et
        print("6. İlanlar kaydediliyor...", file=sys.stderr)
        logger.info("İlanlar kaydediliyor...")
        new_count = await scraper.save_new_listings(listings)
        print(f"7. {new_count} yeni ilan kaydedildi", file=sys.stderr)
        logger.info(f"{new_count} yeni ilan kaydedildi")
        
        if scraper:
            print("8. Tarayıcı kapatılıyor...", file=sys.stderr)
            logger.info("Tarayıcı kapatılıyor...")
            await scraper.close_browser()
            print("9. Tamamlandı!", file=sys.stderr)
            logger.info("Tamamlandı!")
        
        return {
            "message": "Scraping tamamlandı",
            "total_scraped": len(listings),
            "new_listings_added": new_count,
            "listings": [
                {
                    "title": l.get("title", "Bilinmeyen"),
                    "price": l.get("price", 0),
                    "brand": l.get("brand"),
                    "model": l.get("model"),
                    "city": l.get("city"),
                } for l in listings[:10]  # İlk 10'unu göster
            ]
        }
    except Exception as e:
        print(f"HATA: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        logger.error(f"Scraping hatası: {e}", exc_info=True)
        if scraper:
            try:
                await scraper.close_browser()
            except:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping başarısız: {str(e)}"
        )

