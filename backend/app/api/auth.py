from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.api.dependencies import get_current_user

router = APIRouter()


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Email kontrolü
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kayıtlı"
        )
    
    # Yeni kullanıcı oluştur
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Kullanıcıyı bul
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Şifreyi doğrula
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesabınız aktif değil"
        )
    
    # Son giriş zamanını güncelle
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Token oluştur
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Mevcut kullanıcı bilgilerini döndür"""
    return current_user


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Şifre sıfırlama talebi oluştur.
    NOT: Gerçek uygulamada email gönderilir, şimdilik token döndürüyoruz.
    """
    user = db.query(User).filter(User.email == request.email).first()
    
    # Güvenlik: Kullanıcı var olmasa bile aynı yanıtı ver
    if not user:
        return {
            "message": "Eğer bu email kayıtlıysa, şifre sıfırlama bağlantısı gönderildi.",
            "success": True
        }
    
    # Reset token oluştur (32 karakter)
    reset_token = secrets.token_urlsafe(32)
    
    # Token'ı kaydet (1 saat geçerli)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    # NOT: Gerçek uygulamada burada email gönderilir
    # Şimdilik token'ı döndürüyoruz (development için)
    return {
        "message": "Şifre sıfırlama bağlantısı gönderildi.",
        "success": True,
        # Development için token'ı göster (Production'da kaldırılmalı)
        "reset_token": reset_token,
        "expires_in": "1 saat"
    }


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Şifreyi sıfırla.
    """
    # Token'ı kontrol et
    user = db.query(User).filter(User.reset_token == request.token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz veya süresi dolmuş sıfırlama bağlantısı"
        )
    
    # Token süresi dolmuş mu?
    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sıfırlama bağlantısının süresi dolmuş"
        )
    
    # Şifreyi güncelle
    user.password_hash = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {
        "message": "Şifreniz başarıyla güncellendi",
        "success": True
    }


@router.get("/verify-reset-token/{token}")
async def verify_reset_token(token: str, db: Session = Depends(get_db)):
    """
    Reset token'ın geçerli olup olmadığını kontrol et.
    """
    user = db.query(User).filter(User.reset_token == token).first()
    
    if not user:
        return {"valid": False, "message": "Geçersiz token"}
    
    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        return {"valid": False, "message": "Token süresi dolmuş"}
    
    return {"valid": True, "email": user.email}

