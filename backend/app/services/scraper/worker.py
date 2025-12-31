import asyncio
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.scraper.scraper import ArabaComScraper
from app.core.config import settings

logger = logging.getLogger(__name__)

class ScraperWorker:
    def __init__(self):
        self.running = False
        self.scraper = None
    
    async def start(self):
        """Scraper worker'ı başlat"""
        self.running = True
        logger.info("Scraper worker başlatıldı")
        
        while self.running:
            try:
                db = SessionLocal()
                try:
                    scraper = ArabaComScraper(db)
                    await scraper.init_browser()
                    
                    # İlanları çek
                    listings = await scraper.scrape_listings()
                    
                    # Yeni ilanları kaydet
                    new_count = await scraper.save_new_listings(listings)
                    
                    await scraper.close_browser()
                    
                    logger.info(f"Tarama tamamlandı. {len(listings)} ilan bulundu, {new_count} yeni ilan kaydedildi")
                    
                finally:
                    db.close()
                
                # Bekleme süresi
                await asyncio.sleep(settings.SCRAPER_INTERVAL_SECONDS)
                
            except Exception as e:
                logger.error(f"Scraper worker hatası: {e}")
                await asyncio.sleep(settings.SCRAPER_INTERVAL_SECONDS)
    
    def stop(self):
        """Scraper worker'ı durdur"""
        self.running = False
        logger.info("Scraper worker durduruldu")

