"""
Otomatik tarama scheduler servisi
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.filter import Filter
from app.models.listing import Listing
from app.models.user import User
from app.services.scraper.scraper import ArabaComScraper
from app.services.telegram import telegram_service

logger = logging.getLogger(__name__)

class SchedulerService:
    _instance: Optional['SchedulerService'] = None
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
    @classmethod
    def get_instance(cls) -> 'SchedulerService':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def start(self):
        """Scheduler'ı başlat"""
        if self.is_running:
            logger.info("Scheduler zaten çalışıyor")
            return
            
        logger.info("Scheduler başlatılıyor...")
        
        # Her dakika aktif filtreleri kontrol et
        self.scheduler.add_job(
            self._check_and_run_scans,
            IntervalTrigger(minutes=1),
            id='check_scans',
            replace_existing=True
        )
        
        # Her gün gece 3'te eski ilanları temizle
        self.scheduler.add_job(
            self._cleanup_old_listings,
            IntervalTrigger(hours=24),
            id='cleanup_old_listings',
            replace_existing=True
        )
        
        # Her 6 saatte favori fiyatlarını kontrol et
        self.scheduler.add_job(
            self._check_favorite_prices,
            IntervalTrigger(hours=6),
            id='check_favorite_prices',
            replace_existing=True
        )
        
        # Başlangıçta bir kez temizlik yap
        self.scheduler.add_job(
            self._cleanup_old_listings,
            'date',
            run_date=datetime.utcnow() + timedelta(seconds=30),
            id='initial_cleanup'
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("Scheduler başlatıldı ✅")
        
    async def stop(self):
        """Scheduler'ı durdur"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Scheduler durduruldu")
    
    async def _cleanup_old_listings(self):
        """30 günden eski ilanları temizle"""
        db = SessionLocal()
        try:
            from app.models.favorite import Favorite
            
            # 30 günden eski ilanları bul
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Önce bu ilanlara ait favorileri sil
            old_listing_ids = db.query(Listing.id).filter(
                Listing.scraped_at < cutoff_date
            ).all()
            old_ids = [lid[0] for lid in old_listing_ids]
            
            if old_ids:
                # Favorileri sil
                fav_deleted = db.query(Favorite).filter(
                    Favorite.listing_id.in_(old_ids)
                ).delete(synchronize_session=False)
                
                # Eski ilanları sil
                deleted_count = db.query(Listing).filter(
                    Listing.id.in_(old_ids)
                ).delete(synchronize_session=False)
                
                db.commit()
                logger.info(f"Temizlik: {deleted_count} eski ilan silindi (30+ gün), {fav_deleted} favori temizlendi")
            else:
                logger.info("Temizlenecek eski ilan bulunamadı")
                
        except Exception as e:
            logger.error(f"Eski ilan temizleme hatası: {e}")
            db.rollback()
        finally:
            db.close()
            
    async def _check_and_run_scans(self):
        """Zamanı gelen taramaları çalıştır"""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            
            # Otomatik tarama aktif ve zamanı gelmiş filtreleri bul
            filters_to_scan = db.query(Filter).filter(
                Filter.auto_scan_enabled == True,
                Filter.is_active == True,
                (Filter.next_scan_at == None) | (Filter.next_scan_at <= now)
            ).all()
            
            if not filters_to_scan:
                return
                
            logger.info(f"Taranacak {len(filters_to_scan)} filtre bulundu")
            
            for filter_obj in filters_to_scan:
                try:
                    await self._run_scan_for_filter(db, filter_obj)
                except Exception as e:
                    logger.error(f"Filtre {filter_obj.id} taranırken hata: {e}")
                    
        except Exception as e:
            logger.error(f"Tarama kontrolü sırasında hata: {e}")
        finally:
            db.close()
            
    async def _run_scan_for_filter(self, db: Session, filter_obj: Filter):
        """Belirli bir filtre için tarama yap"""
        logger.info(f"Filtre taranıyor: {filter_obj.name} (ID: {filter_obj.id})")
        
        # Her tarama için yeni scraper oluştur
        scraper = ArabaComScraper(db)
        
        try:
            # Scraper'ı başlat
            await scraper.init_browser()
            
            # Filtrenin kriterlerini al
            search_params = filter_obj.criteria or {}
            
            # Tarama yap
            listings = await scraper.scrape_listings(search_params)
            
            # Yeni ilanları kaydet
            new_count = 0
            for listing_data in listings:
                # Aynı URL'den ilan var mı kontrol et
                existing = db.query(Listing).filter(
                    Listing.source_url == listing_data.get("source_url")
                ).first()
                
                if not existing:
                    new_listing = Listing(
                        title=listing_data.get("title", ""),
                        price=listing_data.get("price", 0),
                        source_url=listing_data.get("source_url", ""),
                        images=listing_data.get("images", []),
                        year=listing_data.get("year"),
                        brand=listing_data.get("brand"),
                        model=listing_data.get("model"),
                        city=listing_data.get("city"),
                        fuel_type=listing_data.get("fuel_type"),
                        transmission=listing_data.get("transmission"),
                        mileage=listing_data.get("mileage"),
                        damage_info=listing_data.get("damage_info"),
                        is_new=True,
                        user_id=filter_obj.user_id,
                        filter_id=filter_obj.id
                    )
                    db.add(new_listing)
                    new_count += 1
            
            # Filtre istatistiklerini güncelle
            now = datetime.utcnow()
            filter_obj.last_scan_at = now
            filter_obj.next_scan_at = now + timedelta(minutes=filter_obj.scan_interval)
            filter_obj.total_scans = (filter_obj.total_scans or 0) + 1
            filter_obj.new_listings_found = (filter_obj.new_listings_found or 0) + new_count
            
            db.commit()
            
            logger.info(f"Filtre {filter_obj.name}: {len(listings)} ilan bulundu, {new_count} yeni ilan kaydedildi")
            
            # Telegram bildirimi gönder
            if new_count > 0:
                await self._send_telegram_notification(db, filter_obj, new_count, listings[:5])
            
        except Exception as e:
            logger.error(f"Tarama hatası: {e}")
            # Yine de next_scan_at'ı güncelle ki sürekli hata vermesin
            filter_obj.next_scan_at = datetime.utcnow() + timedelta(minutes=filter_obj.scan_interval)
            db.commit()
        finally:
            await scraper.close_browser()
            
    async def _send_telegram_notification(
        self, 
        db: Session, 
        filter_obj: Filter, 
        new_count: int, 
        listings: list
    ):
        """Yeni ilanlar için Telegram bildirimi gönder"""
        try:
            # Kullanıcıyı al
            user = db.query(User).filter(User.id == filter_obj.user_id).first()
            if not user:
                return
            
            # Telegram bildirimi aktif mi?
            if not user.telegram_enabled or not user.telegram_chat_id:
                return
            
            # Bildirim gönder
            success = await telegram_service.send_new_listings_notification(
                chat_id=user.telegram_chat_id,
                filter_name=filter_obj.name,
                new_count=new_count,
                listings=listings
            )
            
            if success:
                logger.info(f"Telegram bildirimi gönderildi: {user.telegram_chat_id}")
            else:
                logger.warning(f"Telegram bildirimi gönderilemedi: {user.telegram_chat_id}")
                
        except Exception as e:
            logger.error(f"Telegram bildirimi gönderilirken hata: {e}")

    async def trigger_manual_scan(self, filter_id: int) -> dict:
        """Manuel tarama tetikle"""
        db = SessionLocal()
        try:
            filter_obj = db.query(Filter).filter(Filter.id == filter_id).first()
            if not filter_obj:
                return {"success": False, "message": "Filtre bulunamadı"}
                
            await self._run_scan_for_filter(db, filter_obj)
            return {"success": True, "message": "Tarama tamamlandı"}
        except Exception as e:
            logger.error(f"Manuel tarama hatası: {e}")
            return {"success": False, "message": str(e)}
        finally:
            db.close()
    
    async def _check_favorite_prices(self):
        """Favori ilanların fiyat değişimini kontrol et"""
        from app.models.favorite import Favorite
        import aiohttp
        from bs4 import BeautifulSoup
        import re
        
        db = SessionLocal()
        try:
            # Tüm favorileri al
            favorites = db.query(Favorite).all()
            
            if not favorites:
                return
            
            logger.info(f"{len(favorites)} favori için fiyat kontrolü başlıyor...")
            
            updated_count = 0
            
            async with aiohttp.ClientSession() as session:
                for fav in favorites:
                    try:
                        listing = db.query(Listing).filter(Listing.id == fav.listing_id).first()
                        if not listing or not listing.source_url:
                            continue
                        
                        # Siteden güncel fiyatı çek
                        async with session.get(
                            listing.source_url,
                            headers={"User-Agent": "Mozilla/5.0"},
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status != 200:
                                continue
                            
                            html = await response.text()
                            soup = BeautifulSoup(html, 'lxml')
                            
                            # Fiyatı bul
                            new_price = None
                            price_elem = soup.find('span', class_='product-price')
                            if price_elem:
                                price_text = price_elem.get_text(strip=True)
                                price_num = re.sub(r'[^\d]', '', price_text)
                                if price_num:
                                    new_price = float(price_num)
                            
                            if new_price and new_price != listing.price:
                                # Fiyat değişmiş!
                                old_price = listing.price
                                
                                # Listing'i güncelle
                                listing.price = new_price
                                
                                # Favori geçmişine ekle
                                history = fav.price_history or []
                                history.append({
                                    "price": new_price,
                                    "date": datetime.utcnow().isoformat(),
                                    "old_price": old_price
                                })
                                fav.price_history = history
                                fav.last_checked_at = datetime.utcnow()
                                
                                updated_count += 1
                                logger.info(f"Fiyat değişimi: {listing.title[:30]} - {old_price} -> {new_price}")
                                
                                # Fiyat düştüyse Telegram bildirimi gönder
                                if new_price < old_price:
                                    user = db.query(User).filter(User.id == fav.user_id).first()
                                    if user and user.telegram_enabled and user.telegram_chat_id:
                                        try:
                                            await telegram_service.send_price_drop_notification(
                                                chat_id=user.telegram_chat_id,
                                                listing_title=listing.title,
                                                old_price=old_price,
                                                new_price=new_price,
                                                url=listing.source_url
                                            )
                                        except Exception as te:
                                            logger.error(f"Fiyat düşüşü bildirimi gönderilemedi: {te}")
                            
                    except Exception as e:
                        logger.debug(f"Fiyat kontrol hatası: {e}")
                        continue
            
            db.commit()
            logger.info(f"Fiyat kontrolü tamamlandı: {updated_count} güncelleme")
            
        except Exception as e:
            logger.error(f"Favori fiyat kontrolü hatası: {e}")
            db.rollback()
        finally:
            db.close()


# Global scheduler instance
scheduler_service = SchedulerService.get_instance()

