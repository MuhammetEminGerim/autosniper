"""
License API Endpoints
Handles license activation, validation, and status
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.license import LicenseManager
from app.models.license import License
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter()

# Pydantic schemas
class LicenseActivateRequest(BaseModel):
    license_key: str

class LicenseResponse(BaseModel):
    success: bool
    message: str
    license_info: Optional[dict] = None

class LicenseStatusResponse(BaseModel):
    is_active: bool
    package_type: str
    expires_at: str
    days_remaining: int
    hardware_id: str

@router.post("/activate", response_model=LicenseResponse)
async def activate_license(
    request: LicenseActivateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Lisans key'i aktif et
    """
    try:
        # Hardware ID al
        hardware_id = LicenseManager.get_hardware_id()
        
        # Lisans key'i doğrula
        is_valid, message, license_data = LicenseManager.validate_license_key(
            request.license_key,
            hardware_id
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Database'de var mı kontrol et
        existing = db.query(License).filter(
            License.license_key == request.license_key
        ).first()
        
        if existing:
            # Zaten aktif
            if existing.is_active:
                return LicenseResponse(
                    success=True,
                    message="Lisans zaten aktif",
                    license_info={
                        "package_type": existing.package_type,
                        "expires_at": existing.expires_at.isoformat(),
                        "days_remaining": existing.days_remaining
                    }
                )
            else:
                # Deaktif edilmiş
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bu lisans deaktif edilmiş"
                )
        
        # Yeni lisans kaydı oluştur
        new_license = License(
            license_key=request.license_key,
            hardware_id=hardware_id,
            package_type=license_data["package"],
            issued_at=datetime.fromisoformat(license_data["issued_at"]),
            expires_at=datetime.fromisoformat(license_data["expires_at"]),
            user_id=current_user.id if current_user else None
        )
        
        db.add(new_license)
        db.commit()
        db.refresh(new_license)
        
        return LicenseResponse(
            success=True,
            message=f"Lisans başarıyla aktif edildi! {new_license.days_remaining} gün geçerli.",
            license_info={
                "package_type": new_license.package_type,
                "expires_at": new_license.expires_at.isoformat(),
                "days_remaining": new_license.days_remaining
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aktivasyon hatası: {str(e)}"
        )

@router.get("/status", response_model=LicenseStatusResponse)
async def get_license_status(
    db: Session = Depends(get_db)
):
    """
    Mevcut lisans durumunu getir
    """
    try:
        # Hardware ID al
        hardware_id = LicenseManager.get_hardware_id()
        
        # Bu bilgisayar için aktif lisans bul
        license = db.query(License).filter(
            License.hardware_id == hardware_id,
            License.is_active == True
        ).first()
        
        if not license:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aktif lisans bulunamadı"
            )
        
        # Süre dolmuş mu kontrol et
        if license.is_expired:
            license.is_active = False
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Lisans süresi dolmuş"
            )
        
        return LicenseStatusResponse(
            is_active=license.is_active,
            package_type=license.package_type,
            expires_at=license.expires_at.isoformat(),
            days_remaining=license.days_remaining,
            hardware_id=license.hardware_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Durum kontrolü hatası: {str(e)}"
        )

@router.get("/info")
async def get_license_info(db: Session = Depends(get_db)):
    """
    Lisans bilgilerini getir (detaylı)
    """
    try:
        hardware_id = LicenseManager.get_hardware_id()
        
        license = db.query(License).filter(
            License.hardware_id == hardware_id,
            License.is_active == True
        ).first()
        
        if not license:
            return {
                "has_license": False,
                "hardware_id": hardware_id,
                "message": "Lisans bulunamadı. Lütfen lisans key'inizi girin."
            }
        
        return {
            "has_license": True,
            "is_active": license.is_active,
            "is_expired": license.is_expired,
            "package_type": license.package_type,
            "issued_at": license.issued_at.isoformat(),
            "expires_at": license.expires_at.isoformat(),
            "activated_at": license.activated_at.isoformat(),
            "days_remaining": license.days_remaining,
            "hardware_id": license.hardware_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bilgi getirme hatası: {str(e)}"
        )

@router.get("/hardware-id")
async def get_hardware_id():
    """
    Bu bilgisayarın hardware ID'sini getir
    """
    return {
        "hardware_id": LicenseManager.get_hardware_id()
    }
