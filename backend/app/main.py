from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, filters, listings, websocket, test, favorites, admin, quick_search
from app.api import settings as settings_api
from app.core.database import engine, Base
from app.services.scheduler import scheduler_service
import logging

logger = logging.getLogger(__name__)

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü yönetimi"""
    # Başlangıç
    logger.info("AutoSniper başlatılıyor...")
    await scheduler_service.start()
    logger.info("Scheduler başlatıldı ✅")
    
    yield
    
    # Kapanış
    logger.info("AutoSniper kapatılıyor...")
    await scheduler_service.stop()
    logger.info("Scheduler durduruldu ✅")


app = FastAPI(
    title="AutoSniper API",
    description="İkinci el araç piyasası fırsat yakalama sistemi",
    version="1.0.0",
    lifespan=lifespan
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(filters.router, prefix="/api/filters", tags=["filters"])
app.include_router(listings.router, prefix="/api/listings", tags=["listings"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])
app.include_router(test.router, prefix="/api/test", tags=["test"])
app.include_router(quick_search.router, prefix="/api", tags=["quick-search"])
app.include_router(favorites.router, tags=["favorites"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["settings"])
app.include_router(admin.router)  # Admin panel endpoints

@app.get("/")
async def root():
    return {"message": "AutoSniper API", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint for Railway"""
    from datetime import datetime
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

