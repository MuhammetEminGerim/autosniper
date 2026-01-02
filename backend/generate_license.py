"""
AutoSniper License Generator
Müşteriler için lisans key oluştur
"""
from app.core.license import LicenseManager
import sys

def generate_license():
    print("=== AutoSniper Lisans Oluşturucu ===\n")
    
    # Hardware ID al
    hw_id = input("Müşterinin Hardware ID'si: ").strip()
    
    if not hw_id:
        print("❌ Hardware ID gerekli!")
        return
    
    # Paket seç
    print("\nPaket Seçin:")
    print("1. Monthly (₺49 - 30 gün)")
    print("2. Yearly (₺299 - 365 gün)")
    print("3. Lifetime (₺999 - ömür boyu)")
    
    choice = input("\nSeçim (1/2/3): ").strip()
    
    package_map = {
        "1": ("monthly", "Monthly", "30 gün"),
        "2": ("yearly", "Yearly", "365 gün"),
        "3": ("lifetime", "Lifetime", "ömür boyu")
    }
    
    if choice not in package_map:
        print("❌ Geçersiz seçim!")
        return
    
    package_type, package_name, duration = package_map[choice]
    
    # Lisans oluştur
    print(f"\n🔄 {package_name} lisans oluşturuluyor...")
    license_key = LicenseManager.generate_license_key(hw_id, package_type)
    
    # Doğrula
    is_valid, message, data = LicenseManager.validate_license_key(license_key, hw_id)
    
    if is_valid:
        print("\n✅ Lisans başarıyla oluşturuldu!\n")
        print("=" * 60)
        print(f"Hardware ID: {hw_id}")
        print(f"Paket: {package_name} ({duration})")
        print(f"Lisans Key:\n{license_key}")
        print("=" * 60)
        
        # Email template
        print("\n📧 Müşteriye Gönderilecek Email:")
        print("-" * 60)
        print(f"""
Merhaba,

AutoSniper lisansınız hazır!

Lisans Key:
{license_key}

Paket: {package_name} ({duration})
Başlangıç: {data['issued_at']}
Bitiş: {data['expires_at']}

Kullanım:
1. AutoSniper'ı açın
2. Lisans ekranında key'i yapıştırın
3. "Aktif Et" tıklayın

İyi kullanımlar!

AutoSniper Destek
support@autosniper.com
        """)
        print("-" * 60)
        
        # Dosyaya kaydet
        filename = f"license_{hw_id[:8]}_{package_type}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Hardware ID: {hw_id}\n")
            f.write(f"Paket: {package_name}\n")
            f.write(f"Lisans Key: {license_key}\n")
        
        print(f"\n💾 Lisans dosyaya kaydedildi: {filename}")
    else:
        print(f"\n❌ Hata: {message}")

if __name__ == "__main__":
    try:
        generate_license()
    except KeyboardInterrupt:
        print("\n\nİptal edildi.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
