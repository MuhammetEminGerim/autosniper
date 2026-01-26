from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database - SQLite for desktop, PostgreSQL for server
    DATABASE_URL: str = "sqlite:///./autosniper.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 gün
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    def get_cors_origins(self) -> List[str]:
        """CORS origins'i environment'a göre döndür"""
        if self.ENVIRONMENT == "production":
            # Production'da sadece belirtilen origin'ler
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        
        # Development için tüm localhost varyasyonları
        return [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost",
            "http://localhost:80",
            "http://127.0.0.1:3000",
            "http://127.0.0.1",
        ]
    
    # Scraper
    SCRAPER_INTERVAL_SECONDS: int = 30
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_HEADLESS: bool = False
    SCRAPER_TIMEOUT: int = 30000
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

