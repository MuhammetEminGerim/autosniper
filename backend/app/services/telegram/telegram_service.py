"""
Telegram Bot Bildirim Servisi

Telegram Bot API kullanarak mesaj gönderir.
%100 Ücretsiz!

Kurulum:
1. Telegram'da @BotFather'a git
2. /newbot komutu ile yeni bot oluştur
3. Bot token'ını al
4. TELEGRAM_BOT_TOKEN env değişkenini ayarla
"""

import os
import logging
import aiohttp
from typing import Optional, List

logger = logging.getLogger(__name__)


class TelegramService:
    """Telegram bot bildirim servisi"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.api_base = "https://api.telegram.org/bot"
        self._initialized = False
        
    def initialize(self) -> bool:
        """Telegram bot'u başlat"""
        if self._initialized:
            return True
            
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not configured. Telegram notifications disabled.")
            return False
        
        self._initialized = True
        logger.info("Telegram service initialized successfully")
        return True
    
    @property
    def is_configured(self) -> bool:
        """Bot yapılandırılmış mı?"""
        return bool(self.bot_token)
    
    async def send_message(self, chat_id: str, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Telegram mesajı gönder
        
        Args:
            chat_id: Alıcı chat ID (kullanıcı ID veya grup ID)
            message: Gönderilecek mesaj
            parse_mode: Mesaj formatı (Markdown veya HTML)
            
        Returns:
            bool: Başarılı ise True
        """
        if not self.is_configured:
            logger.warning("Telegram bot not configured")
            return False
        
        try:
            url = f"{self.api_base}{self.bot_token}/sendMessage"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": False
                }) as response:
                    result = await response.json()
                    
                    if result.get("ok"):
                        logger.info(f"Telegram message sent to {chat_id}")
                        return True
                    else:
                        logger.error(f"Telegram API error: {result.get('description')}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def get_bot_info(self) -> Optional[dict]:
        """Bot bilgilerini al"""
        if not self.is_configured:
            return None
            
        try:
            url = f"{self.api_base}{self.bot_token}/getMe"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    result = await response.json()
                    
                    if result.get("ok"):
                        return result.get("result")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None
    
    async def send_new_listings_notification(
        self, 
        chat_id: str, 
        filter_name: str, 
        new_count: int, 
        listings: List[dict]
    ) -> bool:
        """
        Yeni ilan bildirimi gönder
        
        Args:
            chat_id: Alıcı chat ID
            filter_name: Filtre adı
            new_count: Yeni ilan sayısı
            listings: İlan listesi (max 5 adet gösterilir)
        """
        # Mesaj oluştur
        message = f"🚗 *{filter_name}* filtrenizde *{new_count}* yeni ilan bulundu!\n\n"
        
        # İlk 5 ilanı ekle
        for i, listing in enumerate(listings[:5], 1):
            title = listing.get("title", "İlan")
            price = listing.get("price", 0)
            price_str = f"{price:,.0f} TL".replace(",", ".")
            url = listing.get("source_url", "")
            
            message += f"*{i}.* {title}\n"
            message += f"   💰 {price_str}\n"
            if url:
                message += f"   🔗 [İlana Git]({url})\n"
            message += "\n"
        
        if new_count > 5:
            message += f"_... ve {new_count - 5} ilan daha_\n\n"
        
        message += "📱 Detaylar için uygulamayı açın."
        
        return await self.send_message(chat_id, message)
    
    async def send_price_drop_notification(
        self,
        chat_id: str,
        listing_title: str,
        old_price: float,
        new_price: float,
        url: str
    ) -> bool:
        """
        Fiyat düşüşü bildirimi gönder
        
        Args:
            chat_id: Alıcı chat ID
            listing_title: İlan başlığı
            old_price: Eski fiyat
            new_price: Yeni fiyat
            url: İlan URL'i
        """
        change = old_price - new_price
        change_pct = (change / old_price) * 100
        
        old_price_str = f"{old_price:,.0f}".replace(",", ".")
        new_price_str = f"{new_price:,.0f}".replace(",", ".")
        change_str = f"{change:,.0f}".replace(",", ".")
        
        message = f"📉 *Fiyat Düşüşü!*\n\n"
        message += f"🚗 {listing_title}\n\n"
        message += f"💰 ~{old_price_str} TL~ → *{new_price_str} TL*\n"
        message += f"📉 *{change_str} TL* indirim (-%{change_pct:.1f})\n\n"
        
        if url:
            message += f"🔗 [İlana Git]({url})"
        
        return await self.send_message(chat_id, message)
    
    async def send_test_message(self, chat_id: str) -> bool:
        """Test mesajı gönder"""
        message = (
            "🎉 *Tebrikler!*\n\n"
            "Telegram bildirimleriniz başarıyla yapılandırıldı.\n\n"
            "Artık şu bildirimleri alacaksınız:\n"
            "• 🆕 Yeni ilan bildirimleri\n"
            "• 📉 Fiyat düşüşü bildirimleri\n\n"
            "🚗 _AutoSniper_"
        )
        return await self.send_message(chat_id, message)


# Singleton instance
telegram_service = TelegramService()

