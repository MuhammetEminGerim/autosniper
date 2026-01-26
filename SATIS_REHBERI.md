# AutoSniper Satış Rehberi

## 🎯 IBAN ile Satış Modeli

### Fiyat Listesi
- **Aylık**: ₺299 (30 gün)
- **Yıllık**: ₺1.999 (365 gün)
- **Lifetime**: ₺4.999 (süresiz)

### Müşteri Akışı
1. Müşteri ilan gösterir → IBAN'a havale yapar
2. Müşteri Hardware ID'sini size gönderir
3. Siz lisans key oluşturup gönderirsiniz
4. Müşteri programı aktive eder

## 🛠️ Lisans Oluşturma

### 1. Script ile Lisans Oluştur
```bash
python license_generator.py
```

### 2. Manuel Lisans Oluşturma
```python
from backend.app.core.license import LicenseManager

# Müşteri hardware ID'si ile lisans oluştur
hw_id = "MUSTERI-HARDWARE-ID"
license_key = LicenseManager.generate_license_key(hw_id, custom_days=30)
print(f"Lisans: {license_key}")
```

## 📧 Müşteriye Gönderilecek Mesaj Şablonu

```
Merhaba [Müşteri Adı],

Ödemeniz alındı, teşekkürler!

📦 Paket: [Aylık/Yıllık/Lifetime]
💰 Ücret: ₺[Fiyat]
🔑 Lisans Key: AUTOSNIPER-XXXX-XXXX-XXXX-XXXX

Aktivasyon için:
1. AutoSniper programını açın
2. Lisans anahtarı bölümüne yukarıdaki key'i girin
3. Aktive butonuna tıklayın

İyi kullanmalar!

Destek için: [Telefon/WhatsApp]
```

## 💡 İpuçları

### Müşteri Hardware ID'si Nasıl Alınır?
1. Müşteri programı açar
2. Lisans aktivasyon sayfasında Hardware ID yazar
3. Müşteri bu ID'yi size gönderir

### Lisans Key Formatı
- Format: AUTOSNIPER-{checksum}-{encoded}
- Örnek: AUTOSNIPER-A1B2C3D4-K2VsdG93ZGZzZ2ZmZ2ZmZw==
- Hardware ID kilitli (başka bilgisayarda çalışmaz)

## 🚀 Avantajlar

✅ **Sıfır maliyet** - Sunucu, hosting yok
✅ **Offline çalışır** - İnternet gerekmez  
✅ **Tek seferlik ödeme** - Müşteri sever
✅ **Kurulum kolay** - Tek dosya
✅ **Güvenli** - Hardware ID kilitli

## 📞 Destek

Müşteriler için destek:
- Telefon/WhatsApp: [Numaranız]
- E-posta: [E-postanız]
- Çalışma saatleri: [Saatleriniz]

---

*AutoSniper - İkinci el araç fırsatlarını ilk siz yakalayın!*
