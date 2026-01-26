# AutoSniper Lisans Generator - Test
# Manuel olarak lisans oluşturma

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.license import LicenseManager

def test_license_generation():
    print("=== AutoSniper Lisans Generator Test ===\n")
    
    # Mevcut bilgisayarın hardware ID'si
    current_hw_id = LicenseManager.get_hardware_id()
    print(f"Mevcut Hardware ID: {current_hw_id}")
    
    # Test müşteri bilgileri
    customer_name = "Test Müşteri"
    customer_hw_id = current_hw_id  # Mevcut hardware ID kullan
    package = "lifetime"
    days = 9999
    price = 4999
    
    print(f"Müşteri: {customer_name}")
    print(f"Hardware ID: {customer_hw_id}")
    print(f"Paket: {package}")
    print(f"Fiyat: ₺{price}")
    print()
    
    # Lisans oluştur
    license_key = LicenseManager.generate_license_key(
        hardware_id=customer_hw_id,
        package_type=package
    )
    
    print(f"Oluşturulan Lisans Key: {license_key}")
    print()
    
    # Doğrula
    is_valid, message, data = LicenseManager.validate_license_key(license_key)
    
    print(f"Durum: {'✅ Geçerli' if is_valid else '❌ Geçersiz'}")
    print(f"Mesaj: {message}")
    
    if data:
        print(f"Paket: {data.get('package')}")
        print(f"Oluşturulma: {data.get('issued_at')}")
        print(f"Bitiş: {data.get('expires_at')}")
    
    print(f"\n{'='*50}")
    
    # Müşteri mesajı
    print(f"\n📧 Müşteriye gönderilecek mesaj:")
    print(f"Merhaba {customer_name},")
    print(f"Ödemeniz alındı, teşekkürler!")
    print(f"Lisans anahtarınız: {license_key}")
    print(f"Aktivasyon için programı açıp lisans key'i girin.")
    print(f"İyi kullanmalar!")

if __name__ == "__main__":
    test_license_generation()
