# AutoSniper Lisans Generator
# IBAN ile satış için müşteri lisansları oluşturma script'i

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.license import LicenseManager

def generate_license_for_customer():
    print("=== AutoSniper Lisans Generator ===\n")
    
    # Müşteri bilgileri
    customer_name = input("Müşteri Adı: ")
    customer_hw_id = input("Hardware ID: ").strip().upper()
    
    # Paket seçimi
    print("\nPaketler:")
    print("1. Aylık (30 gün) - ₺299")
    print("2. Yıllık (365 gün) - ₺1.999") 
    print("3. Lifetime (süresiz) - ₺4.999")
    print("4. Özel gün sayısı")
    
    choice = input("Seçim (1-4): ")
    
    if choice == "1":
        package = "monthly"
        days = 30
        price = 299
    elif choice == "2":
        package = "yearly"
        days = 365
        price = 1999
    elif choice == "3":
        package = "lifetime"
        days = 9999
        price = 4999
    elif choice == "4":
        days = int(input("Gün sayısı: "))
        package = "custom"
        price = int(input("Fiyat (₺): "))
    else:
        print("Geçersiz seçim!")
        return
    
    # Lisans oluştur
    license_key = LicenseManager.generate_license_key(
        hardware_id=customer_hw_id,
        package_type=package if package != "custom" else "monthly",
        custom_days=days if package == "custom" else None
    )
    
    # Doğrula
    is_valid, message, data = LicenseManager.validate_license_key(license_key)
    
    print(f"\n{'='*50}")
    print(f"Müşteri: {customer_name}")
    print(f"Paket: {package}")
    print(f"Fiyat: ₺{price}")
    print(f"Hardware ID: {customer_hw_id}")
    print(f"Lisans Key: {license_key}")
    print(f"Durum: {'✅ Geçerli' if is_valid else '❌ Geçersiz'}")
    print(f"Mesaj: {message}")
    print(f"{'='*50}")
    
    # Kopyala için
    try:
        import pyperclip
        pyperclip.copy(license_key)
        print("✅ Lisans key panoya kopyalandı!")
    except ImportError:
        print("⚠️ Pyperclip kurulu değil. Manuel kopyalayın.")
    
    # Müşteri mesajı
    print(f"\n📧 Müşteriye gönderilecek mesaj:")
    print(f"Merhaba {customer_name},")
    print(f"Ödemeniz alındı, teşekkürler!")
    print(f"Lisans anahtarınız: {license_key}")
    print(f"Aktivasyon için programı açıp lisans key'i girin.")
    print(f"İyi kullanmalar!")

if __name__ == "__main__":
    generate_license_for_customer()
