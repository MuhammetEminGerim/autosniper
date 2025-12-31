"""
İlk admin kullanıcısı oluşturma scripti

Kullanım:
    python create_admin.py

Bu script ilk admin kullanıcısını oluşturur.
Email: admin@autosniper.com
Şifre: admin123 (değiştirmeyi unutma!)
"""

import sys
import os

# Backend klasörünü path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User

def create_admin_user():
    db = SessionLocal()
    
    try:
        # Admin kullanıcısı var mı kontrol et
        admin = db.query(User).filter(User.email == "admin@autosniper.com").first()
        
        if admin:
            print("❌ Admin kullanıcısı zaten mevcut!")
            print(f"   Email: {admin.email}")
            print(f"   Admin: {admin.is_admin}")
            return
        
        # Yeni admin kullanıcısı oluştur
        admin_user = User(
            email="admin@autosniper.com",
            password_hash=get_password_hash("admin123"),
            is_admin=True,
            is_active=True,
            subscription_tier="pro",  # Admin'e pro paket ver
            daily_search_limit=9999,
            max_filters=9999
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin kullanıcısı başarıyla oluşturuldu!")
        print(f"   Email: admin@autosniper.com")
        print(f"   Şifre: admin123")
        print(f"   ID: {admin_user.id}")
        print("")
        print("⚠️  ÖNEMLİ: İlk girişten sonra şifreyi değiştir!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Admin kullanıcısı oluşturuluyor...")
    print("")
    create_admin_user()
