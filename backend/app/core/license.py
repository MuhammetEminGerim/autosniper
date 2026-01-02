"""
AutoSniper License System
Offline license validation with hardware ID locking
"""
import hashlib
import uuid
import platform
import json
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from cryptography.fernet import Fernet
import base64

class LicenseManager:
    """Offline license management system"""
    
    # Secret key for encryption (değiştir production'da!)
    SECRET_KEY = b'AutoSniper2026SecretKeyChangeThis!!'
    
    @staticmethod
    def get_hardware_id() -> str:
        """
        Bilgisayarın benzersiz kimliğini oluştur
        MAC address + CPU info kombinasyonu
        """
        try:
            # MAC address al
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0, 2*6, 2)][::-1])
            
            # Platform bilgisi
            system_info = f"{platform.system()}-{platform.machine()}"
            
            # Hash oluştur
            combined = f"{mac}-{system_info}"
            hardware_id = hashlib.sha256(combined.encode()).hexdigest()[:16]
            
            return hardware_id.upper()
        except Exception as e:
            # Fallback: UUID
            return str(uuid.uuid4())[:16].upper()
    
    @staticmethod
    def _get_cipher():
        """Encryption cipher oluştur"""
        # Secret key'den Fernet key oluştur
        key = base64.urlsafe_b64encode(LicenseManager.SECRET_KEY[:32])
        return Fernet(key)
    
    @staticmethod
    def generate_license_key(
        hardware_id: str,
        package_type: str = "monthly",
        custom_days: Optional[int] = None
    ) -> str:
        """
        Lisans key oluştur
        
        Args:
            hardware_id: Bilgisayar kimliği
            package_type: "monthly", "yearly", "lifetime"
            custom_days: Özel gün sayısı (opsiyonel)
        
        Returns:
            Lisans key (AUTOSNIPER-XXXX-XXXX-XXXX-XXXX)
        """
        # Bitiş tarihini hesapla
        now = datetime.now()
        
        if custom_days:
            expire_date = now + timedelta(days=custom_days)
        elif package_type == "monthly":
            expire_date = now + timedelta(days=30)
        elif package_type == "yearly":
            expire_date = now + timedelta(days=365)
        elif package_type == "lifetime":
            expire_date = now + timedelta(days=9999)  # ~27 yıl
        else:
            raise ValueError(f"Invalid package type: {package_type}")
        
        # License data
        license_data = {
            "hardware_id": hardware_id,
            "package": package_type,
            "issued_at": now.strftime("%Y-%m-%d"),
            "expires_at": expire_date.strftime("%Y-%m-%d"),
            "version": "1.0"
        }
        
        # JSON string'e çevir
        json_str = json.dumps(license_data, separators=(',', ':'))
        
        # Base64 encode
        encoded = base64.b64encode(json_str.encode()).decode()
        
        # Checksum ekle
        checksum = hashlib.md5(encoded.encode()).hexdigest()[:8]
        
        # Full key: AUTOSNIPER-{checksum}-{encoded}
        key = f"AUTOSNIPER-{checksum}-{encoded}"
        
        return key
    
    @staticmethod
    def validate_license_key(
        license_key: str,
        current_hardware_id: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Lisans key'i doğrula
        
        Args:
            license_key: Lisans key
            current_hardware_id: Mevcut hardware ID (None ise otomatik al)
        
        Returns:
            (is_valid, message, license_data)
        """
        try:
            # Hardware ID al
            if current_hardware_id is None:
                current_hardware_id = LicenseManager.get_hardware_id()
            
            # Key formatını kontrol et
            if not license_key.startswith("AUTOSNIPER-"):
                return False, "Geçersiz lisans formatı", None
            
            # Parse key: AUTOSNIPER-{checksum}-{encoded}
            parts = license_key.split("-", 2)  # Max 3 parts
            if len(parts) != 3:
                return False, "Geçersiz lisans formatı", None
            
            checksum = parts[1]
            encoded = parts[2]
            
            # Checksum doğrula
            expected_checksum = hashlib.md5(encoded.encode()).hexdigest()[:8]
            if checksum != expected_checksum:
                return False, "Lisans key bozuk (checksum mismatch)", None
            
            # Base64 decode
            try:
                decoded = base64.b64decode(encoded).decode()
                license_data = json.loads(decoded)
            except Exception as e:
                return False, f"Lisans key geçersiz: {str(e)}", None
            
            # Hardware ID kontrol et
            if license_data.get("hardware_id") != current_hardware_id:
                return False, "Bu lisans başka bir bilgisayar için geçerli", None
            
            # Tarih kontrol et
            expire_date_str = license_data.get("expires_at")
            expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d")
            
            if datetime.now() > expire_date:
                days_expired = (datetime.now() - expire_date).days
                return False, f"Lisans süresi {days_expired} gün önce doldu", license_data
            
            # Kalan gün hesapla
            days_remaining = (expire_date - datetime.now()).days
            
            return True, f"Lisans geçerli ({days_remaining} gün kaldı)", license_data
            
        except Exception as e:
            return False, f"Doğrulama hatası: {str(e)}", None
    
    @staticmethod
    def get_license_info(license_key: str) -> Optional[Dict]:
        """
        Lisans bilgilerini al (doğrulama yapmadan)
        """
        try:
            parts = license_key.replace("AUTOSNIPER-", "").replace("-", "")
            encrypted = base64.urlsafe_b64decode(parts)
            cipher = LicenseManager._get_cipher()
            decrypted = cipher.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except:
            return None


# Test fonksiyonu
if __name__ == "__main__":
    print("=== AutoSniper License System Test ===\n")
    
    # Hardware ID al
    hw_id = LicenseManager.get_hardware_id()
    print(f"Hardware ID: {hw_id}\n")
    
    # Test lisansları oluştur
    print("1. Monthly License:")
    monthly_key = LicenseManager.generate_license_key(hw_id, "monthly")
    print(f"   Key: {monthly_key}")
    valid, msg, data = LicenseManager.validate_license_key(monthly_key)
    print(f"   Valid: {valid} - {msg}\n")
    
    print("2. Yearly License:")
    yearly_key = LicenseManager.generate_license_key(hw_id, "yearly")
    print(f"   Key: {yearly_key}")
    valid, msg, data = LicenseManager.validate_license_key(yearly_key)
    print(f"   Valid: {valid} - {msg}\n")
    
    print("3. Lifetime License:")
    lifetime_key = LicenseManager.generate_license_key(hw_id, "lifetime")
    print(f"   Key: {lifetime_key}")
    valid, msg, data = LicenseManager.validate_license_key(lifetime_key)
    print(f"   Valid: {valid} - {msg}\n")
    
    # Geçersiz test
    print("4. Invalid Hardware ID Test:")
    valid, msg, data = LicenseManager.validate_license_key(monthly_key, "INVALID-HW-ID")
    print(f"   Valid: {valid} - {msg}\n")
    
    print("5. Invalid Key Test:")
    valid, msg, data = LicenseManager.validate_license_key("AUTOSNIPER-XXXX-XXXX-XXXX-XXXX")
    print(f"   Valid: {valid} - {msg}\n")
