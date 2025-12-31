from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.filter import Filter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama başarısız",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user


async def check_rate_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Günlük arama limitini kontrol eder.
    Limit aşılırsa 429 hatası döner.
    """
    # Günlük reset kontrolü
    if current_user.last_reset_date < date.today():
        current_user.daily_search_count = 0
        current_user.last_reset_date = date.today()
        db.commit()
        db.refresh(current_user)
    
    # Limit kontrolü
    if current_user.daily_search_count >= current_user.daily_search_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Günlük arama limitiniz doldu",
                "current": current_user.daily_search_count,
                "limit": current_user.daily_search_limit,
                "reset_time": "Gece 00:00",
                "upgrade_url": "/pricing"
            }
        )
    
    # Sayacı artır
    current_user.daily_search_count += 1
    db.commit()
    db.refresh(current_user)
    
    return current_user


async def check_filter_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Maksimum filtre sayısını kontrol eder.
    Limit aşılırsa 403 hatası döner.
    """
    filter_count = db.query(Filter).filter(
        Filter.user_id == current_user.id
    ).count()
    
    if filter_count >= current_user.max_filters:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Maksimum filtre sayısına ulaştınız",
                "current": filter_count,
                "limit": current_user.max_filters,
                "upgrade_url": "/pricing"
            }
        )
    
    return current_user
