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
# Models'den import ediyoruz ki hepsi yüklensin
from app.models import User, License, Filter, Listing, Notification, Favorite

def create_admin_user():
    db = SessionLocal()

    try:
        # Admin kullanıcısı var mı kontrol et
        admin = db.query(User).filter(User.email == "admin@autosniper.com").first()

        if admin:
            print("[!] Admin kullanicisi zaten mevcut!")
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

        print("[OK] Admin kullanicisi basariyla olusturuldu!")
        print(f"   Email: admin@autosniper.com")
        print(f"   Sifre: admin123")
        print(f"   ID: {admin_user.id}")
        print("")
        print("[!] ONEMLI: Ilk giristen sonra sifreyi degistir!")

    except Exception as e:
        print(f"[ERROR] Hata: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Admin kullanicisi olusturuluyor...")
    create_admin_user()
