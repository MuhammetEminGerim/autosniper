from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.filter import Filter
from app.models.listing import Listing
from app.api.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Admin middleware
async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin yetkisi gerekli"
        )
    return current_user

# Schemas
class UserUpdateRequest(BaseModel):
    subscription_tier: Optional[str] = None
    daily_search_limit: Optional[int] = None
    max_filters: Optional[int] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserStatsResponse(BaseModel):
    id: int
    email: str
    subscription_tier: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]
    filter_count: int
    daily_search_count: int
    daily_search_limit: int
    max_filters: int

class SystemStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_filters: int
    total_listings: int
    new_users_today: int
    new_users_this_week: int
    searches_today: int
    free_users: int
    basic_users: int
    pro_users: int

# Endpoints

@router.get("/users", response_model=List[UserStatsResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Tüm kullanıcıları listele"""
    users = db.query(User).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        filter_count = db.query(Filter).filter(Filter.user_id == user.id).count()
        result.append(UserStatsResponse(
            id=user.id,
            email=user.email,
            subscription_tier=user.subscription_tier,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login,
            filter_count=filter_count,
            daily_search_count=user.daily_search_count,
            daily_search_limit=user.daily_search_limit,
            max_filters=user.max_filters
        ))
    
    return result

@router.get("/users/{user_id}", response_model=UserStatsResponse)
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Kullanıcı detayı"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    filter_count = db.query(Filter).filter(Filter.user_id == user.id).count()
    
    return UserStatsResponse(
        id=user.id,
        email=user.email,
        subscription_tier=user.subscription_tier,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        last_login=user.last_login,
        filter_count=filter_count,
        daily_search_count=user.daily_search_count,
        daily_search_limit=user.daily_search_limit,
        max_filters=user.max_filters
    )

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    update_data: UserUpdateRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Kullanıcı bilgilerini güncelle"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    # Paket değişikliği
    if update_data.subscription_tier:
        user.subscription_tier = update_data.subscription_tier
        # Paket limitlerini otomatik ayarla
        if update_data.subscription_tier == "free":
            user.daily_search_limit = 50
            user.max_filters = 5
        elif update_data.subscription_tier == "basic":
            user.daily_search_limit = 500
            user.max_filters = 20
        elif update_data.subscription_tier == "pro":
            user.daily_search_limit = 2000
            user.max_filters = 999
    
    if update_data.daily_search_limit is not None:
        user.daily_search_limit = update_data.daily_search_limit
    
    if update_data.max_filters is not None:
        user.max_filters = update_data.max_filters
    
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    
    if update_data.is_admin is not None:
        user.is_admin = update_data.is_admin
    
    db.commit()
    db.refresh(user)
    
    return {"message": "Kullanıcı güncellendi", "user_id": user.id}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Kullanıcıyı sil"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    # Kendi hesabını silemesin
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Kendi hesabınızı silemezsiniz")
    
    db.delete(user)
    db.commit()
    
    return {"message": "Kullanıcı silindi"}

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Sistem istatistikleri"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_filters = db.query(Filter).count()
    total_listings = db.query(Listing).count()
    
    # Bugün kayıt olan kullanıcılar
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    new_users_today = db.query(User).filter(User.created_at >= today).count()
    
    # Bu hafta kayıt olan kullanıcılar
    week_ago = datetime.now() - timedelta(days=7)
    new_users_this_week = db.query(User).filter(User.created_at >= week_ago).count()
    
    # Bugünkü aramalar
    searches_today = db.query(func.sum(User.daily_search_count)).scalar() or 0
    
    # Paket dağılımı
    free_users = db.query(User).filter(User.subscription_tier == "free").count()
    basic_users = db.query(User).filter(User.subscription_tier == "basic").count()
    pro_users = db.query(User).filter(User.subscription_tier == "pro").count()
    
    return SystemStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_filters=total_filters,
        total_listings=total_listings,
        new_users_today=new_users_today,
        new_users_this_week=new_users_this_week,
        searches_today=searches_today,
        free_users=free_users,
        basic_users=basic_users,
        pro_users=pro_users
    )
