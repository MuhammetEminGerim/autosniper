"""
Arabam.com Sandbox API Client
Cloudflare bypass için web scraping yerine resmi API kullanır
"""
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ArabamAPIClient:
    """Arabam.com Sandbox API Client"""
    
    BASE_URL = "http://sandbox.arabamd.com/api/v1"
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """HTTP session oluştur veya mevcut olanı döndür"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'AutoSniper/1.0'
                }
            )
        return self._session
    
    async def close(self):
        """HTTP session'ı kapat"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_listings(
        self, 
        take: int = 20, 
        skip: int = 0,
        sort: int = 1,  # 1=Tarih (Yeniden Eskiye), 2=Fiyat (Düşükten Yükseğe), 3=Yıl (Yeniden Eskiye)
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
        category_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        İlan listesini çek
        
        Args:
            take: Kaç ilan çekilecek (default: 20)
            skip: Kaç ilan atlanacak (pagination için)
            sort: Sıralama (1=Tarih, 2=Fiyat, 3=Yıl)
            min_price: Minimum fiyat
            max_price: Maximum fiyat
            min_year: Minimum yıl
            max_year: Maximum yıl
            min_date: Minimum tarih (YYYY-MM-DD)
            max_date: Maximum tarih (YYYY-MM-DD)
            category_id: Kategori ID
        
        Returns:
            İlan listesi
        """
        try:
            session = await self._get_session()
            
            # Query parameters
            params = {
                'take': take,
                'skip': skip,
                'sort': sort
            }
            
            # Optional filters
            if min_price:
                params['minPrice'] = min_price
            if max_price:
                params['maxPrice'] = max_price
            if min_year:
                params['minYear'] = min_year
            if max_year:
                params['maxYear'] = max_year
            if min_date:
                params['minDate'] = min_date
            if max_date:
                params['maxDate'] = max_date
            if category_id:
                params['categoryId'] = category_id
            
            url = f"{self.BASE_URL}/listing"
            logger.info(f"Arabam API isteği: {url} - Params: {params}")
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Arabam API'den {len(data)} ilan geldi")
                    return data
                else:
                    logger.error(f"Arabam API hatası: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Arabam API isteği başarısız: {e}")
            return []
    
    async def get_detail(self, listing_id: int) -> Optional[Dict[str, Any]]:
        """
        İlan detayını çek
        
        Args:
            listing_id: İlan ID
        
        Returns:
            İlan detayı veya None
        """
        try:
            session = await self._get_session()
            
            url = f"{self.BASE_URL}/detail"
            params = {'id': listing_id}
            
            logger.info(f"Arabam API detay isteği: ID={listing_id}")
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"İlan detayı alındı: ID={listing_id}")
                    return data
                else:
                    logger.error(f"Arabam API detay hatası: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Arabam API detay isteği başarısız: {e}")
            return None
    
    def parse_listing(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        API'den gelen raw data'yı parse et
        
        Args:
            raw_data: API'den gelen ham veri
        
        Returns:
            Parse edilmiş ilan verisi
        """
        try:
            # Image URL'yi düzelt (800x600 resolution)
            photo = raw_data.get('photo', '')
            if '{0}' in photo:
                photo = photo.replace('{0}', '800x600')
            
            return {
                'id': raw_data.get('id'),
                'title': raw_data.get('title', ''),
                'price': raw_data.get('price', 0),
                'year': raw_data.get('modelYear', 0),
                'km': raw_data.get('mileage', 0),
                'location': raw_data.get('location', ''),
                'date': raw_data.get('dateFormatted', ''),
                'photo': photo,
                'category': raw_data.get('category', ''),
                'url': f"https://www.arabam.com/ilan/{raw_data.get('id')}",
                'source': 'arabam_api'
            }
        except Exception as e:
            logger.error(f"Parse hatası: {e}")
            return {}
