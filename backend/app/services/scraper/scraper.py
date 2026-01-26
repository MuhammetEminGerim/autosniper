import asyncio
import re
import sys
import aiohttp
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Browser, Page
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from app.models.listing import Listing
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ArabaComScraper:
    # Browser timeout (saniye)
    BROWSER_TIMEOUT = 60000  # 60 saniye
    PAGE_TIMEOUT = 30000     # 30 saniye
    MAX_CONCURRENT_REQUESTS = 5  # Aynı anda max istek sayısı
    
    def __init__(self, db: Session):
        self.db = db
        self.base_url = "https://www.arabam.com"
        self.browser: Browser = None
        self.page: Page = None
        self.playwright = None
        self.context = None
        self._http_session = None
        self._semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)
    
    async def init_browser(self):
        """Tarayıcıyı başlat - timeout korumalı"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # Eski moda geri döndük ama args ile güçlendireceğiz
                args=[
                    '--headless=new', # YENİ GİZLİ MOD (Bot tespiti çok daha zor)
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled', # Otomasyon izlerini gizle
                    '--ignore-certificate-errors',
                    '--no-first-run',
                    '--no-service-autorun',
                    '--password-store=basic',
                    '--use-mock-keychain',
                ],
                timeout=self.BROWSER_TIMEOUT
            )
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='tr-TR',
                timezone_id='Europe/Istanbul',
                # Bot tespitini aşmak için ekstra headers
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            )
            # Sayfa timeout'ları ayarla
            self.context.set_default_timeout(self.PAGE_TIMEOUT)
            self.context.set_default_navigation_timeout(self.PAGE_TIMEOUT)
            
            self.page = await self.context.new_page()
            
            # Bot tespitini aşmak için JavaScript'i override et
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.chrome = {
                    runtime: {}
                };
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            logger.info("Tarayıcı başarıyla başlatıldı")
        except Exception as e:
            logger.error(f"Tarayıcı başlatma hatası: {e}")
            await self.close_browser()
            raise
    
    async def close_browser(self):
        """Tarayıcıyı güvenli şekilde kapat - memory leak önleme"""
        try:
            # HTTP session'ı kapat
            await self.close_http_session()
            
            if self.page:
                try:
                    await self.page.close()
                except:
                    pass
                self.page = None
            
            if self.context:
                try:
                    await self.context.close()
                except:
                    pass
                self.context = None
                
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass
                self.browser = None
            
            if self.playwright:
                try:
                    await self.playwright.stop()
                except:
                    pass
                self.playwright = None
                
            logger.info("Tarayıcı ve HTTP session kapatıldı")
        except Exception as e:
            logger.error(f"Tarayıcı kapatma hatası: {e}")
    
    async def scrape_listings(self, search_params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Arabam.com'dan ilanları çek
        """
        if not self.page:
            await self.init_browser()
        
        try:
            # sort=1 = En yeni ilanlar (tarih - yeniden eskiye)
            url = f"{self.base_url}/ikinci-el?sort=1"
            
            if search_params:
                # Filtre kriterlerine göre URL parametreleri ekle
                if search_params.get("brand"):
                    # arabam.com marka formatı: marka-model şeklinde URL path'e eklenir
                    brand = search_params["brand"].lower().replace(" ", "-")
                    url = f"{self.base_url}/ikinci-el/{brand}?sort=1"
                
                if search_params.get("model"):
                    model = search_params["model"].lower().replace(" ", "-")
                    # Eğer marka varsa, model de ekle
                    if search_params.get("brand"):
                        brand = search_params["brand"].lower().replace(" ", "-")
                        url = f"{self.base_url}/ikinci-el/{brand}-{model}?sort=1"
                
                # Query parametreleri
                query_params = []
                
                if search_params.get("min_year"):
                    query_params.append(f"minYear={search_params['min_year']}")
                if search_params.get("max_year"):
                    query_params.append(f"maxYear={search_params['max_year']}")
                if search_params.get("min_price"):
                    query_params.append(f"minPrice={int(search_params['min_price'])}")
                if search_params.get("max_price"):
                    query_params.append(f"maxPrice={int(search_params['max_price'])}")
                if search_params.get("city"):
                    # arabam.com şehir kodları (plaka kodları)
                    city_codes = {
                        "adana": "1", "adıyaman": "2", "afyonkarahisar": "3", "ağrı": "4", 
                        "amasya": "5", "ankara": "6", "antalya": "7", "artvin": "8",
                        "aydın": "9", "balıkesir": "10", "bilecik": "11", "bingöl": "12",
                        "bitlis": "13", "bolu": "14", "burdur": "15", "bursa": "16",
                        "çanakkale": "17", "çankırı": "18", "çorum": "19", "denizli": "20",
                        "diyarbakır": "21", "edirne": "22", "elazığ": "23", "erzincan": "24",
                        "erzurum": "25", "eskişehir": "26", "gaziantep": "27", "giresun": "28",
                        "gümüşhane": "29", "hakkari": "30", "hatay": "31", "ısparta": "32",
                        "mersin": "33", "istanbul": "34", "izmir": "35", "kars": "36",
                        "kastamonu": "37", "kayseri": "38", "kırklareli": "39", "kırşehir": "40",
                        "kocaeli": "41", "konya": "42", "kütahya": "43", "malatya": "44",
                        "manisa": "45", "kahramanmaraş": "46", "mardin": "47", "muğla": "48",
                        "muş": "49", "nevşehir": "50", "niğde": "51", "ordu": "52",
                        "rize": "53", "sakarya": "54", "samsun": "55", "siirt": "56",
                        "sinop": "57", "sivas": "58", "tekirdağ": "59", "tokat": "60",
                        "trabzon": "61", "tunceli": "62", "şanlıurfa": "63", "uşak": "64",
                        "van": "65", "yozgat": "66", "zonguldak": "67", "aksaray": "68",
                        "bayburt": "69", "karaman": "70", "kırıkkale": "71", "batman": "72",
                        "şırnak": "73", "bartın": "74", "ardahan": "75", "iğdır": "76",
                        "yalova": "77", "karabük": "78", "kilis": "79", "osmaniye": "80",
                        "düzce": "81", "İstanbul": "34", "İzmir": "35"
                    }
                    city_name = search_params["city"].lower()
                    city_code = city_codes.get(city_name, "")
                    if city_code:
                        query_params.append(f"city={city_code}")
                if search_params.get("fuel_type"):
                    fuel_map = {"dizel": "2", "benzin": "1", "elektrik": "6", "hibrit": "4", "lpg": "3"}
                    fuel_code = fuel_map.get(search_params["fuel_type"].lower(), "")
                    if fuel_code:
                        query_params.append(f"fuel={fuel_code}")
                if search_params.get("transmission"):
                    trans_map = {"otomatik": "2", "manuel": "1", "yarı otomatik": "3"}
                    trans_code = trans_map.get(search_params["transmission"].lower(), "")
                    if trans_code:
                        query_params.append(f"gear={trans_code}")
                
                if query_params:
                    url += "&" + "&".join(query_params)
            
            print(f"Oluşturulan URL: {url}", file=sys.stderr)
            
            logger.info(f"Scraping başlatılıyor: {url}")
            print(f"URL'ye gidiliyor: {url}", file=sys.stderr)
            
            # Sayfayı yükle - daha uzun bekleme süresi
            try:
                # Önce load event'ini bekle
                await self.page.goto(url, wait_until="load", timeout=90000)
                await asyncio.sleep(2)
                # Sonra networkidle için bekle
                await self.page.wait_for_load_state("networkidle", timeout=30000)
            except Exception as e:
                logger.warning(f"networkidle timeout, domcontentloaded deneniyor: {e}")
                try:
                    await self.page.goto(url, wait_until="domcontentloaded", timeout=90000)
                except Exception as e2:
                    logger.error(f"Sayfa yüklenemedi: {e2}")
                    # Sayfayı tekrar yükle
                    await self.page.reload(wait_until="load", timeout=60000)
            
            # Bot korumasını aşmak için daha uzun bekleme
            await asyncio.sleep(5)
            
            # Lazy loading için sayfayı scroll et - tüm resimlerin yüklenmesi için
            print("Sayfa scroll ediliyor (lazy loading için)...", file=sys.stderr)
            await self.page.evaluate("""
                async () => {
                    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
                    // Sayfanın en altına kadar scroll et
                    const scrollHeight = document.body.scrollHeight;
                    const viewportHeight = window.innerHeight;
                    let currentPosition = 0;
                    
                    while (currentPosition < scrollHeight) {
                        window.scrollTo(0, currentPosition);
                        await delay(300);
                        currentPosition += viewportHeight;
                    }
                    // En alta git
                    window.scrollTo(0, scrollHeight);
                    await delay(500);
                    // Tekrar en başa dön
                    window.scrollTo(0, 0);
                }
            """)
            await asyncio.sleep(5)  # Bot koruması için daha uzun bekleme
            
            page_title = await self.page.title()
            current_url = self.page.url
            page_content = await self.page.content()
            
            logger.info(f"Sayfa başlığı: {page_title}")
            logger.info(f"Mevcut URL: {current_url}")
            logger.info(f"Sayfa içeriği uzunluğu: {len(page_content)} karakter")
            print(f"Sayfa başlığı: {page_title}", file=sys.stderr)
            print(f"Mevcut URL: {current_url}", file=sys.stderr)
            print(f"Sayfa içeriği uzunluğu: {len(page_content)} karakter", file=sys.stderr)
            
            # 503 hatası ve bot koruması kontrolü
            if "503" in page_title or "Backend fetch failed" in page_title or "Sonuç bulunamadı" in page_content:
                logger.error("503 hatası: arabam.com bot koruması aktif. Daha fazla bekleme...")
                await asyncio.sleep(5)
                # Sayfayı yeniden yükle
                try:
                    await self.page.reload(wait_until="load", timeout=60000)
                    await asyncio.sleep(3)
                    page_content = await self.page.content()
                    page_title = await self.page.title()
                    if "503" in page_title or len(page_content) < 5000:
                        logger.error("503 hatası devam ediyor, scraping iptal ediliyor")
                        return []
                except Exception as e:
                    logger.error(f"Sayfa yeniden yüklenemedi: {e}")
                    return []
            
            if len(page_content) < 5000:
                logger.error("Sayfa çok kısa, hata olabilir")
                return []
            
            print(f"SAYFA BAŞARIYLA YÜKLENDİ: {current_url}", file=sys.stderr)
            
            listings = []
            
            # Yöntem 1: Doğrudan ilan linklerini bul
            # arabam.com GÜNCEL link class'ı: a.link-overlay
            ilan_links = await self.page.query_selector_all("a.link-overlay")
            print(f"Bulunan ilan linki sayısı (a.link-overlay): {len(ilan_links)}", file=sys.stderr)
            
            if len(ilan_links) == 0:
                # Alternatif 1: /ilan/ ve /detay içeren linkler
                ilan_links = await self.page.query_selector_all("a[href*='/ilan/'][href*='/detay']")
                print(f"Alternatif ilan linki sayısı (/ilan/+/detay): {len(ilan_links)}", file=sys.stderr)
            
            if len(ilan_links) == 0:
                # Alternatif 2: Sadece /ilan/ içeren linkler
                ilan_links = await self.page.query_selector_all("a[href*='/ilan/']")
                print(f"Alternatif ilan linki sayısı (/ilan/): {len(ilan_links)}", file=sys.stderr)
            
            # Önce sayfadaki ilan kartlarını bul
            # arabam.com'un GÜNCEL yapısını kullan (2024)
            # Doğru selector: table.listing-table içindeki tr.listing-list-item
            listing_cards = await self.page.query_selector_all('table.listing-table tr.listing-list-item')
            print(f"Listing card sayısı (table.listing-table tr.listing-list-item): {len(listing_cards)}", file=sys.stderr)
            
            if len(listing_cards) == 0:
                # Alternatif 1: Sadece tr.listing-list-item
                listing_cards = await self.page.query_selector_all('tr.listing-list-item')
                print(f"Alternatif listing card sayısı (tr.listing-list-item): {len(listing_cards)}", file=sys.stderr)
            
            if len(listing_cards) == 0:
                # Alternatif 2: Tüm table row'ları (son çare)
                listing_cards = await self.page.query_selector_all('table.listing-table tbody tr')
                print(f"Alternatif table row sayısı (tbody tr): {len(listing_cards)}", file=sys.stderr)
            
            # İlk kartın TÜM HTML'ini göster
            if len(listing_cards) > 0:
                first_card = listing_cards[0]
                card_html = await first_card.inner_html()
                print(f"=== İLK KART TÜM HTML ({len(card_html)} karakter) ===", file=sys.stderr)
                print(card_html[:4000], file=sys.stderr)
                print(f"=== HTML SONU ===", file=sys.stderr)
            
            # Önce tüm unique URL'leri ve bilgilerini topla
            url_data = {}  # URL -> {texts: [], elements: []}
            
            for link in ilan_links:
                try:
                    href = await link.get_attribute("href")
                    if not href or "/ilan/" not in href:
                        continue
                    
                    # URL'yi düzelt
                    if href.startswith("/"):
                        full_url = self.base_url + href
                    else:
                        full_url = href
                    
                    # Geçersiz URL'leri atla
                    skip_patterns = ["/satildi", "/login", "/kayit", "/filtre", "/compare", "/favori"]
                    if any(pattern in full_url.lower() for pattern in skip_patterns):
                        continue
                    
                    # URL'ye ait bilgileri topla
                    if full_url not in url_data:
                        url_data[full_url] = {"texts": [], "href": href}
                    
                    # Link metnini al
                    link_text = await link.inner_text()
                    if link_text and link_text.strip():
                        url_data[full_url]["texts"].append(link_text.strip())
                    
                    # Parent element'i bul ve içeriğini al
                    try:
                        parent = await link.evaluate_handle("""
                            (el) => {
                                let p = el.closest('tr, [class*="listing-item"], [class*="card"], article, li');
                                if (!p) p = el.parentElement?.parentElement?.parentElement;
                                return p;
                            }
                        """)
                        if parent:
                            parent_elem = await parent.as_element()
                            if parent_elem:
                                parent_text = await parent_elem.inner_text()
                                if parent_text:
                                    url_data[full_url]["parent_text"] = parent_text
                                parent_html = await parent_elem.inner_html()
                                if parent_html:
                                    url_data[full_url]["parent_html"] = parent_html
                    except:
                        pass
                        
                except Exception as e:
                    continue
            
            print(f"Toplam {len(url_data)} benzersiz ilan URL'si bulundu", file=sys.stderr)
            
            # Listing card'lardan (table row) direkt veri çek - daha güvenilir
            print(f"Listing card'lardan veri çekiliyor...", file=sys.stderr)
            
            for card in listing_cards[:25]:
                try:
                    # img tag'ini bul
                    img = await card.query_selector('img.listing-image, img[class*="listing"]')
                    if not img:
                        img = await card.query_selector('img')
                    
                    if img:
                        # Önce src, yoksa data-src, yoksa data-original kontrol et
                        src = await img.get_attribute("src") or ""
                        if not src or "placeholder" in src.lower() or "1x1" in src:
                            src = await img.get_attribute("data-src") or await img.get_attribute("data-original") or ""
                        alt = await img.get_attribute("alt") or ""
                        
                        # Link'i bul
                        link = await card.query_selector('a[href*="/ilan/"]')
                        href = await link.get_attribute("href") if link else ""
                        
                        if href and alt:
                            full_url = self.base_url + href if href.startswith("/") else href
                            
                            # Fiyatı bul
                            price_elem = await card.query_selector('[class*="price"], .listing-price, td:last-child')
                            price_text = await price_elem.inner_text() if price_elem else ""
                            price = self.parse_price(price_text) if price_text else 0
                            
                            # Fiyat bulunamadıysa tüm text'ten çıkar
                            if price == 0:
                                card_text = await card.inner_text()
                                price = self.extract_price_from_text(card_text, "")
                            
                            # Şehir: Detay sayfasından çekilecek (şimdilik boş bırak)
                            city = self.extract_city(alt)  # Başlıktan dene
                            
                            # Resim URL'sinin geçerli olup olmadığını kontrol et
                            valid_image = False
                            if src:
                                # arbstorage, mncdn veya herhangi bir jpg/png/webp
                                if any(kw in src.lower() for kw in ["arbstorage", "mncdn", "ilanfoto", "cdn"]):
                                    valid_image = True
                                elif any(ext in src.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                                    if not any(bad in src.lower() for bad in ["placeholder", "icon", "logo", "1x1", "spinner"]):
                                        valid_image = True
                            
                            listing_data = {
                                "title": alt[:200],
                                "price": price,
                                "source_url": full_url,
                                "year": self.extract_year(alt),
                                "brand": self.extract_brand(alt),
                                "model": None,
                                "city": city,
                                "fuel_type": self.extract_fuel_type(alt),
                                "transmission": self.extract_transmission(alt),
                                "mileage": None,
                                "description": alt,
                                "images": [src] if valid_image else [],
                                "damage_info": None
                            }
                            
                            listings.append(listing_data)
                            print(f"İlan eklendi: {alt[:45]} - {price} TL - {len(listing_data['images'])} resim", file=sys.stderr)
                except Exception as e:
                    print(f"Card parse hatası: {e}", file=sys.stderr)
                    continue
            
            # Eğer listing_cards'dan yeterli veri gelmezse, eski yönteme devam et
            if len(listings) < 5:
                print(f"Card'lardan {len(listings)} ilan geldi, URL yöntemiyle devam ediliyor...", file=sys.stderr)
                
                # Sayfadaki tüm resimleri ve alt text'leri topla
                all_images = {}
                try:
                    img_elements = await self.page.query_selector_all('img[src*="arbstorage"]')
                    for img in img_elements:
                        try:
                            src = await img.get_attribute("src") or ""
                            alt = await img.get_attribute("alt") or ""
                            id_match = re.search(r'/(\d{7,10})/', src)
                            if id_match:
                                ilan_id = id_match.group(1)
                                if ilan_id not in all_images:
                                    all_images[ilan_id] = {"images": [], "alt": alt}
                                if src not in all_images[ilan_id]["images"]:
                                    all_images[ilan_id]["images"].append(src)
                        except:
                            continue
                except:
                    pass
                
                # URL yöntemi
                for full_url, data in list(url_data.items())[:50]:
                    try:
                        href = data["href"]
                        texts = data.get("texts", [])
                        parent_text = data.get("parent_text", "")
                        
                        # URL'den ilan ID'sini çıkar
                        ilan_id_match = re.search(r'/(\d{7,10})(?:/|$|\?)', href)
                        ilan_id = ilan_id_match.group(1) if ilan_id_match else None
                        
                        # Başlık ve Resim
                        title = ""
                        images = []
                        
                        if ilan_id and ilan_id in all_images:
                            images = all_images[ilan_id]["images"][:3]
                            title = all_images[ilan_id]["alt"]
                        
                        if not title or len(title) < 10:
                            title = self.extract_title_from_url(href)
                        
                        if not title or len(title) < 10:
                            continue
                        
                        # Fiyat
                        price = 0.0
                        for txt in texts:
                            if "TL" in txt or "₺" in txt:
                                price = self.parse_price(txt)
                                if price > 10000:
                                    break
                        
                        if price == 0 and parent_text:
                            price = self.extract_price_from_text(parent_text, "")
                        
                        listing_data = {
                            "title": title[:200],
                            "price": price,
                            "source_url": full_url,
                            "year": self.extract_year(title),
                            "brand": self.extract_brand(title),
                            "model": None,
                            "city": self.extract_city(title),
                            "fuel_type": self.extract_fuel_type(title),
                            "transmission": self.extract_transmission(title),
                            "mileage": None,
                            "description": title,
                            "images": images[:3] if images else [],
                            "damage_info": None
                        }
                        
                        listings.append(listing_data)
                        print(f"İlan eklendi: {title[:40]} - {price} TL - {len(images)} resim", file=sys.stderr)
                        
                    except Exception as e:
                        continue
            
            # TÜM ilanlar için detay sayfasından ek bilgi çek (resim, şehir, hasar, km)
            # Hasar bilgisi (boya-değişen-tramer) tüm ilanlar için gerekli
            listings_needing_details = [
                l for l in listings 
                if l.get("source_url")  # URL'si olan tüm ilanlar
            ]
            
            if listings_needing_details:
                print(f"{len(listings_needing_details)} ilan için detay bilgisi çekiliyor (paralel)...", file=sys.stderr)
                
                # Paralel olarak detay bilgilerini çek
                tasks = [self.fetch_detail_info(l["source_url"]) for l in listings_needing_details]
                detail_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Sonuçları ilanlara ata
                for i, listing in enumerate(listings_needing_details):
                    if i < len(detail_results) and isinstance(detail_results[i], dict):
                        detail = detail_results[i]
                        
                        # Resim yoksa detaydan al
                        if not listing.get("images") or len(listing.get("images", [])) == 0:
                            if detail.get("images"):
                                listing["images"] = detail["images"]
                                print(f"  + Resim eklendi: {listing['title'][:30]} ({len(detail['images'])} resim)", file=sys.stderr)
                        
                        # Şehir yoksa detaydan al
                        if not listing.get("city") and detail.get("city"):
                            listing["city"] = detail["city"]
                        
                        # Kilometre bilgisi
                        if detail.get("mileage"):
                            listing["mileage"] = detail["mileage"]
                        
                        # Hasar bilgisi
                        if detail.get("damage_info"):
                            listing["damage_info"] = detail["damage_info"]
                
                logger.info(f"Detay bilgileri çekildi: {len(listings_needing_details)} ilan")
            
            logger.info(f"Toplam {len(listings)} ilan çıkarıldı")
            return listings
            
        except Exception as e:
            logger.error(f"Scraping hatası: {e}", exc_info=True)
            return []
    
    def extract_title_from_url(self, url: str) -> str:
        """URL'den araç başlığı çıkar"""
        try:
            # URL örneği: /ilan/galeriden-satilik-renault-symbol-1-5-dci-joy/galeriden-renault-symbol-1-5-dci-joy-2018-model-bursa/33861099
            # Son parça: ID (33861099)
            # Ondan önceki parça: Gerçek başlık
            
            parts = [p for p in url.split("/") if p and not p.isdigit()]
            
            # "ilan" kelimesini çıkar
            if "ilan" in parts:
                parts.remove("ilan")
            
            # Son anlamlı parçayı al (ID'den önceki)
            if not parts:
                return ""
            
            # Genelde son parça en detaylı başlık
            title_part = parts[-1] if parts else ""
            
            # Kebab-case'i parçala
            words = title_part.split("-")
            
            # Temizlenecek kelimeler
            skip_words = ["galeriden", "sahibinden", "satilik", "kiralik", "takas", "model", "detay"]
            
            clean_words = []
            for word in words:
                # Şehir isimlerini atla
                cities = ["istanbul", "ankara", "izmir", "bursa", "adana", "antalya", "konya", "gaziantep", "kayseri", "mersin", "eskisehir", "diyarbakir", "samsun", "denizli", "sanliurfa", "malatya", "trabzon", "erzurum"]
                if word.lower() in cities:
                    continue
                # Yılları atla
                if re.match(r'^(19|20)\d{2}$', word):
                    continue
                # Skip listesindeki kelimeleri atla
                if word.lower() in skip_words:
                    continue
                # Çok kısa kelimeleri atla (1, 5 gibi motor hacmi hariç)
                if len(word) < 2:
                    continue
                clean_words.append(word.capitalize())
            
            if clean_words:
                # Tekrarlı kelimeleri kaldır (ardışık)
                unique_words = []
                for word in clean_words:
                    if not unique_words or word.lower() != unique_words[-1].lower():
                        unique_words.append(word)
                return " ".join(unique_words[:7])
            
            return ""
        except:
            return ""
    
    def extract_price_from_text(self, text: str, html: str) -> float:
        """Metinden fiyat çıkar"""
        try:
            # Önce HTML'de fiyat class'ı ara
            price_patterns = [
                r'class="[^"]*price[^"]*"[^>]*>([^<]+)',
                r'class="[^"]*fiyat[^"]*"[^>]*>([^<]+)',
                r'data-price="([\d.,]+)"',
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    price = self.parse_price(match.group(1))
                    if price > 10000:  # Makul bir fiyat
                        return price
            
            # Metin içinde fiyat ara
            # Türk formatı: 1.500.000 TL veya 1,500,000 TL
            text_patterns = [
                r'([\d]{1,3}(?:\.[\d]{3}){2,})\s*(?:TL|₺)',  # 1.500.000 TL
                r'([\d]{1,3}(?:,[\d]{3}){2,})\s*(?:TL|₺)',  # 1,500,000 TL
                r'([\d]{6,})\s*(?:TL|₺)',  # 1500000 TL
                r'(?:TL|₺)\s*([\d]{1,3}(?:\.[\d]{3}){2,})',  # TL 1.500.000
            ]
            
            for pattern in text_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    price = self.parse_price(match.group(1))
                    if price > 10000:
                        return price
            
            # Son çare: Büyük sayıları ara
            all_numbers = re.findall(r'[\d]{1,3}(?:\.[\d]{3}){1,}', text)
            for num_str in all_numbers:
                price = self.parse_price(num_str)
                if 50000 < price < 50000000:  # Makul fiyat aralığı
                    return price
            
            return 0.0
        except:
            return 0.0
    
    async def extract_images_from_element(self, element) -> List[str]:
        """Element içinden resimleri çıkar"""
        images = []
        try:
            img_elements = await element.query_selector_all("img")
            
            for img in img_elements:
                # Tüm olası src attribute'larını kontrol et
                src = (
                    await img.get_attribute("src") or
                    await img.get_attribute("data-src") or
                    await img.get_attribute("data-original") or
                    await img.get_attribute("data-lazy-src")
                )
                
                if not src:
                    continue
                
                # Geçersiz resimleri filtrele
                invalid = ["placeholder", "icon", "logo", "spinner", "loading", "blank", "svg", "gif", "1x1", "pixel", "data:image"]
                if any(kw in src.lower() for kw in invalid):
                    continue
                
                # URL'yi tamamla
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = self.base_url + src
                elif not src.startswith("http"):
                    src = self.base_url + "/" + src
                
                # Sadece resim formatlarını kabul et
                if any(ext in src.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]) or "image" in src.lower():
                    if src not in images:
                        images.append(src)
            
            # Eğer img bulunamadıysa, background-image kontrol et
            if not images:
                html = await element.inner_html()
                bg_patterns = [
                    r'background-image:\s*url\(["\']?([^"\']+)["\']?\)',
                    r'background:\s*url\(["\']?([^"\']+)["\']?\)',
                ]
                for pattern in bg_patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    for src in matches[:3]:
                        if src.startswith("//"):
                            src = "https:" + src
                        elif src.startswith("/"):
                            src = self.base_url + src
                        if src not in images:
                            images.append(src)
        except Exception as e:
            logger.debug(f"Resim çıkarılırken hata: {e}")
        
        return images
    
    def extract_year(self, text: str) -> int:
        """Metinden yıl çıkar"""
        try:
            match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if match:
                year = int(match.group(1))
                if 1980 <= year <= 2025:
                    return year
        except:
            pass
        return None
    
    def extract_brand(self, text: str) -> str:
        """Metinden marka çıkar"""
        brands = [
            "Audi", "BMW", "Mercedes", "Volkswagen", "Ford", "Opel",
            "Renault", "Peugeot", "Fiat", "Toyota", "Honda", "Hyundai",
            "Volvo", "Skoda", "Seat", "Citroen", "Dacia", "Nissan",
            "Kia", "Mazda", "Mitsubishi", "Suzuki", "Chevrolet", "Jeep"
        ]
        text_lower = text.lower()
        for brand in brands:
            if brand.lower() in text_lower:
                return brand
        return None
    
    def extract_city(self, text: str) -> str:
        """Metinden şehir çıkar"""
        cities = [
            "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana",
            "Gaziantep", "Konya", "Kayseri", "Mersin", "Eskişehir", "Samsun",
            "Tekirdağ", "Kastamonu", "Denizli", "Manisa", "Kocaeli", "Sakarya",
            "Trabzon", "Diyarbakır", "Şanlıurfa", "Malatya", "Erzurum", "Aydın",
            "Balıkesir", "Hatay", "Van", "Kahramanmaraş", "Ordu", "Afyonkarahisar",
            "Muğla", "Elazığ", "Mardin", "Aksaray", "Edirne", "Çanakkale",
            "Zonguldak", "Tokat", "Kırıkkale", "Çorum", "Sivas", "Yozgat"
        ]
        text_lower = text.lower()
        for city in cities:
            if city.lower() in text_lower:
                return city
        return None
    
    async def fetch_city_from_detail(self, url: str) -> str:
        """Detay sayfasından şehir bilgisini çek - hızlı HTTP request ile"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"User-Agent": settings.SCRAPER_USER_AGENT}
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # product-location span içeriğini regex ile bul
                        # <span class="product-location">...<span>Merkez Kapaklı, Tekirdağ</span></span>
                        match = re.search(r'class="product-location"[^>]*>.*?<span>([^<]+)</span>', html, re.DOTALL)
                        if match:
                            location_text = match.group(1).strip()
                            if "," in location_text:
                                city = location_text.split(",")[-1].strip()
                                return city
                            return location_text
                        
        except Exception as e:
            pass  # Sessizce devam et
        
        return None
    
    async def _get_http_session(self):
        """Shared HTTP session - connection pooling için"""
        if self._http_session is None or self._http_session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.MAX_CONCURRENT_REQUESTS,
                limit_per_host=self.MAX_CONCURRENT_REQUESTS,
                ttl_dns_cache=300
            )
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            self._http_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": settings.SCRAPER_USER_AGENT}
            )
        return self._http_session
    
    async def close_http_session(self):
        """HTTP session'ı kapat"""
        if self._http_session and not self._http_session.closed:
            await self._http_session.close()
            self._http_session = None
    
    async def fetch_detail_info(self, url: str) -> Dict[str, Any]:
        """Detay sayfasından ek bilgileri çek (resimler, hasar bilgisi, km) - BeautifulSoup ile"""
        
        result = {
            "images": [],
            "damage_info": None,
            "mileage": None,
            "city": None
        }
        
        try:
            # Semaphore ile eşzamanlı istek sayısını sınırla
            async with self._semaphore:
                session = await self._get_http_session()
                async with session.get(url) as response:
                    if response.status != 200:
                        return result
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # 1. Resimleri çek - BeautifulSoup ile
                    images = []
                    
                    # Galeri resimleri
                    for img in soup.find_all('img'):
                        src = img.get('data-src') or img.get('src') or img.get('data-original') or ""
                        if not src:
                            continue
                        # Geçerli araç resmi mi?
                        if any(kw in src.lower() for kw in ["arbstorage", "mncdn", "ilanfoto"]):
                            if not any(bad in src.lower() for bad in ["logo", "icon", "placeholder", "1x1", "pixel"]):
                                if src not in images:
                                    images.append(src)
                    
                    # og:image meta tag
                    og_image = soup.find('meta', property='og:image')
                    if og_image and og_image.get('content'):
                        img_url = og_image['content']
                        if img_url not in images:
                            images.insert(0, img_url)  # Başa ekle
                    
                    result["images"] = images[:5]  # İlk 5 resim
                    
                    # 2. Şehir bilgisi
                    location_elem = soup.find('span', class_='product-location')
                    if location_elem:
                        inner_span = location_elem.find('span')
                        if inner_span:
                            location_text = inner_span.get_text(strip=True)
                            if "," in location_text:
                                result["city"] = location_text.split(",")[-1].strip()
                            else:
                                result["city"] = location_text
                    
                    # 3. Kilometre bilgisi - tablo satırlarından
                    for row in soup.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            label = cells[0].get_text(strip=True).lower()
                            if 'kilometre' in label:
                                km_text = cells[1].get_text(strip=True)
                                km_str = re.sub(r'[^\d]', '', km_text)
                                if km_str:
                                    try:
                                        result["mileage"] = int(km_str)
                                    except:
                                        pass
                                break
                    
                    # 4. Boya-Değişen ve Tramer Bilgisi
                    damage_info = self.parse_damage_info_bs(soup)
                    if damage_info:
                        result["damage_info"] = damage_info
                    
        except Exception as e:
            logger.debug(f"Detay çekme hatası ({url}): {e}")
        
        return result
    
    def parse_damage_info(self, html: str) -> Dict[str, Any]:
        """HTML'den boya-değişen ve tramer bilgisini parse et (regex - eski yöntem)"""
        # BeautifulSoup versiyonu kullanılıyor, bu sadece fallback
        return None
    
    def parse_damage_info_bs(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """BeautifulSoup ile boya-değişen ve tramer bilgisini parse et"""
        import json
        
        damage_info = {
            "original": [],
            "local_painted": [],
            "painted": [],
            "changed": [],
            "unknown": [],
            "tramer_amount": None
        }
        
        try:
            # YENİ: window.damage JavaScript değişkeninden çek (en güvenilir yol)
            found_damage_script = False
            for script in soup.find_all('script'):
                script_text = script.string or ""
                if 'window.damage' in script_text:
                    found_damage_script = True
                    # window.damage = [...] kısmını çıkar
                    match = re.search(r'window\.damage\s*=\s*(\[.*?\]);', script_text, re.DOTALL)
                    if match:
                        try:
                            damage_data = json.loads(match.group(1))
                            
                            # ValueText alanını kullan (en güvenilir)
                            # Örnek: {"ValueText": "original", "ValueDescription": "Orijinal"}
                            value_text_map = {
                                "original": "original",
                                "painted": "painted",
                                "localpainted": "local_painted",
                                "local_painted": "local_painted",
                                "changed": "changed",
                                "replaced": "changed",
                                "unknown": "unknown",
                                "notspecified": "unknown"
                            }
                            
                            for item in damage_data:
                                part_name = item.get("Name", "")
                                # Önce ValueText'e bak (en güvenilir)
                                value_text = str(item.get("ValueText", "")).lower().replace(" ", "")
                                
                                if value_text in value_text_map:
                                    category = value_text_map[value_text]
                                else:
                                    # Fallback: Value sayısını kullan
                                    value = str(item.get("Value", "-1"))
                                    fallback_map = {"0": "unknown", "1": "original", "2": "local_painted", "3": "painted", "4": "changed", "-1": "unknown"}
                                    category = fallback_map.get(value, "unknown")
                                
                                if part_name and part_name not in damage_info[category]:
                                    damage_info[category].append(part_name)
                            
                        except json.JSONDecodeError:
                            pass  # JSON parse hatası - sessizce devam
                        break
            
            # Tramer tutarı - tramer-info class'ından
            tramer_info = soup.find('div', class_='tramer-info')
            if tramer_info:
                tramer_text = tramer_info.get_text(strip=True)
                print(f"Tramer text: {tramer_text}", file=sys.stderr)
                
                # "Tramer tutarı Belirtilmemiş" veya "Tramer tutarı 15.000 TL"
                if 'belirtilmemiş' in tramer_text.lower():
                    damage_info["tramer_amount"] = "Belirtilmemiş"
                else:
                    tramer_match = re.search(r'([\d.,]+)\s*(?:TL|₺)?', tramer_text)
                    if tramer_match:
                        damage_info["tramer_amount"] = tramer_match.group(1).strip() + " TL"
                    else:
                        damage_info["tramer_amount"] = tramer_text.replace("Tramer tutarı", "").strip()
            
            # Alternatif: property-key içinde tramer ara
            if not damage_info["tramer_amount"]:
                tramer_p = soup.find('p', class_='property-key', string=re.compile(r'tramer', re.IGNORECASE))
                if tramer_p:
                    tramer_text = tramer_p.get_text(strip=True)
                    if 'belirtilmemiş' in tramer_text.lower():
                        damage_info["tramer_amount"] = "Belirtilmemiş"
                    else:
                        tramer_match = re.search(r'([\d.,]+)\s*(?:TL|₺)?', tramer_text)
                        if tramer_match:
                            damage_info["tramer_amount"] = tramer_match.group(1).strip() + " TL"
            
            # Eğer herhangi bir bilgi varsa döndür
            if any([
                damage_info["original"],
                damage_info["local_painted"],
                damage_info["painted"],
                damage_info["changed"],
                damage_info["unknown"],
                damage_info["tramer_amount"]
            ]):
                return damage_info
                
        except Exception as e:
            print(f"Damage info parse hatası: {e}", file=sys.stderr)
        
        return None
    
    def extract_fuel_type(self, text: str) -> str:
        """Metinden yakıt tipi çıkar"""
        text_lower = text.lower()
        if any(w in text_lower for w in ["dizel", "diesel"]):
            return "dizel"
        elif any(w in text_lower for w in ["benzin", "petrol"]):
            return "benzin"
        elif any(w in text_lower for w in ["elektrik", "electric"]):
            return "elektrik"
        elif any(w in text_lower for w in ["hibrit", "hybrid"]):
            return "hibrit"
        elif any(w in text_lower for w in ["lpg"]):
            return "lpg"
        return None
    
    def extract_transmission(self, text: str) -> str:
        """Metinden vites tipi çıkar"""
        text_lower = text.lower()
        if any(w in text_lower for w in ["otomatik", "automatic"]):
            return "otomatik"
        elif any(w in text_lower for w in ["manuel", "manual", "düz vites"]):
            return "manuel"
        return None
    
    def parse_price(self, price_text: str) -> float:
        """Fiyat metnini sayıya çevir"""
        try:
            if not price_text:
                return 0.0
            
            # TL, ₺ gibi sembolleri temizle
            price_text = price_text.replace("TL", "").replace("₺", "").replace("tl", "").strip()
            
            # Nokta ve virgülü kontrol et
            dots = price_text.count(".")
            commas = price_text.count(",")
            
            if dots >= 2 or (dots == 1 and len(price_text.split(".")[-1]) == 3):
                # Nokta binlik ayracı (1.500.000 veya 1.500)
                price_text = price_text.replace(".", "")
            elif commas >= 2 or (commas == 1 and len(price_text.split(",")[-1]) == 3):
                # Virgül binlik ayracı (1,500,000 veya 1,500)
                price_text = price_text.replace(",", "")
            elif commas == 1:
                # Virgül ondalık ayracı olabilir (1,5)
                price_text = price_text.replace(",", ".")
            
            # Sadece sayıları al
            price_text = re.sub(r'[^\d.]', '', price_text)
            
            if not price_text:
                return 0.0
            
            return float(price_text)
        except:
            return 0.0
    
    async def save_new_listings(self, listings: List[Dict[str, Any]]):
        """Yeni ilanları veritabanına kaydet - race condition korumalı"""
        from app.models.filter import Filter
        from app.services.filter_matcher import FilterMatcher
        from app.services.websocket.manager import manager
        from sqlalchemy.exc import IntegrityError
        
        new_count = 0
        new_listings = []
        
        # Önce mevcut URL'leri toplu olarak al (performans için)
        existing_urls = set()
        source_urls = [l.get("source_url") for l in listings if l.get("source_url")]
        if source_urls:
            existing = self.db.query(Listing.source_url).filter(
                Listing.source_url.in_(source_urls)
            ).all()
            existing_urls = {e[0] for e in existing}
        
        for listing_data in listings:
            source_url = listing_data.get("source_url")
            if not source_url:
                continue
            
            # Zaten varsa atla
            if source_url in existing_urls:
                continue
            
            try:
                # Yeni listing oluştur
                new_listing = Listing(
                    source_url=source_url,
                    title=listing_data.get("title", "")[:500],  # Max uzunluk
                    price=listing_data.get("price", 0),
                    year=listing_data.get("year"),
                    brand=listing_data.get("brand"),
                    model=listing_data.get("model"),
                    fuel_type=listing_data.get("fuel_type"),
                    transmission=listing_data.get("transmission"),
                    mileage=listing_data.get("mileage"),
                    city=listing_data.get("city"),
                    description=listing_data.get("description"),
                    images=listing_data.get("images", []),
                    damage_info=listing_data.get("damage_info"),
                    is_new=True
                )
                self.db.add(new_listing)
                self.db.flush()
                new_listings.append(new_listing)
                new_count += 1
                existing_urls.add(source_url)  # Listeye ekle ki tekrar eklemesin
            except IntegrityError:
                # Race condition - başka bir process eklemiş
                self.db.rollback()
                logger.warning(f"Duplicate URL atlandı (race condition): {source_url[:50]}")
                continue
        
        if new_count > 0:
            try:
                self.db.commit()
                logger.info(f"{new_count} yeni ilan kaydedildi")
            except IntegrityError:
                self.db.rollback()
                logger.error("Commit sırasında IntegrityError - partial save")
            
            # Yeni ilanları filtrelerle eşleştir ve bildirim gönder
            for new_listing in new_listings:
                all_filters = self.db.query(Filter).filter(Filter.is_active == True).all()
                matching_filters = FilterMatcher.find_matching_filters(new_listing, all_filters)
                
                for filter_obj in matching_filters:
                    await manager.send_personal_message({
                        "type": "new_listing",
                        "message": f"Filtrenize uyan yeni ilan bulundu: {new_listing.title}",
                        "listing": {
                            "id": new_listing.id,
                            "title": new_listing.title,
                            "price": new_listing.price,
                            "source_url": new_listing.source_url,
                        },
                        "filter_id": filter_obj.id,
                        "filter_name": filter_obj.name,
                    }, filter_obj.user_id)
                    
                    logger.info(f"Kullanıcı {filter_obj.user_id} için yeni ilan bildirimi gönderildi: {new_listing.id}")
        
        return new_count
