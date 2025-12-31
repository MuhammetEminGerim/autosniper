from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user
from app.services.telegram import telegram_service

router = APIRouter()


class TelegramSettings(BaseModel):
    telegram_chat_id: Optional[str] = None
    telegram_enabled: bool = False


class TelegramSettingsResponse(BaseModel):
    telegram_chat_id: Optional[str]
    telegram_enabled: bool
    bot_configured: bool
    bot_username: Optional[str] = None
    
    class Config:
        from_attributes = True


class TestTelegramRequest(BaseModel):
    chat_id: str


@router.get("/telegram", response_model=TelegramSettingsResponse)
async def get_telegram_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Telegram bildirim ayarlarını getir"""
    bot_info = await telegram_service.get_bot_info() if telegram_service.is_configured else None
    
    return TelegramSettingsResponse(
        telegram_chat_id=current_user.telegram_chat_id,
        telegram_enabled=current_user.telegram_enabled,
        bot_configured=telegram_service.is_configured,
        bot_username=bot_info.get("username") if bot_info else None
    )


@router.put("/telegram", response_model=TelegramSettingsResponse)
async def update_telegram_settings(
    settings: TelegramSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Telegram bildirim ayarlarını güncelle"""
    
    if settings.telegram_chat_id:
        chat_id = settings.telegram_chat_id.strip()
        current_user.telegram_chat_id = chat_id
    else:
        current_user.telegram_chat_id = None
        settings.telegram_enabled = False  # Chat ID yoksa bildirimi kapat
    
    current_user.telegram_enabled = settings.telegram_enabled
    db.commit()
    db.refresh(current_user)
    
    bot_info = await telegram_service.get_bot_info() if telegram_service.is_configured else None
    
    return TelegramSettingsResponse(
        telegram_chat_id=current_user.telegram_chat_id,
        telegram_enabled=current_user.telegram_enabled,
        bot_configured=telegram_service.is_configured,
        bot_username=bot_info.get("username") if bot_info else None
    )


@router.post("/telegram/test")
async def test_telegram(
    request: TestTelegramRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Test Telegram mesajı gönder.
    """
    if not telegram_service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram bot yapılandırılmamış. TELEGRAM_BOT_TOKEN gerekli."
        )
    
    chat_id = request.chat_id.strip()
    
    success = await telegram_service.send_test_message(chat_id)
    
    if success:
        return {"success": True, "message": "Test mesajı gönderildi!"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mesaj gönderilemedi. Chat ID'yi kontrol edin ve bota /start yazdığınızdan emin olun."
        )


@router.get("/telegram/bot-info")
async def get_bot_info(
    current_user: User = Depends(get_current_user)
):
    """Bot bilgilerini getir"""
    if not telegram_service.is_configured:
        return {"configured": False}
    
    bot_info = await telegram_service.get_bot_info()
    
    if bot_info:
        return {
            "configured": True,
            "username": bot_info.get("username"),
            "first_name": bot_info.get("first_name"),
            "can_join_groups": bot_info.get("can_join_groups", False)
        }
    
    return {"configured": False, "error": "Bot bilgileri alınamadı"}
