# AutoSniper Sorun Giderme

## 🔧 Uygulama Açılmıyor Mu?

### Muhtemel Nedenler ve Çözümler:

### 1. **Backend Başlatma Sorunu**
**Sorun:** Backend servisi başlayamıyor
**Çözüm:**
```bash
# 1. Backend'i manuel test et
cd dist\win-unpacked\resources\backend
autosniper-backend.exe

# 2. Hata çıkarsa Python kütüphaneleri eksiktir
# Çözüm: Geliştirme modunda test et
cd backend
python -m uvicorn app.main:app --port 8000
```

### 2. **Frontend Dosyası Eksik**
**Sorun:** frontend/dist klasörü boş
**Çözüm:**
```bash
cd frontend
npm run build
```

### 3. **Port Çakışması**
**Sorun:** 8000 port'u başka uygulama tarafından kullanılıyor
**Çözüm:**
```bash
# Port'u kontrol et
netstat -ano | findstr :8000

# Kullanılan uygulamayı sonlandır
taskkill /PID [PID] /F
```

### 4. **Windows Defender/Antivirüs**
**Sorun:** Antivirüs engelliyor
**Çözüm:**
- AutoSniper.exe'yi istisna olarak ekle
- Klasörü güvenli olarak işaretle

### 5. **Visual C++ Redistributable**
**Sorun:** Sistem kütüphaneleri eksik
**Çözüm:**
- Microsoft Visual C++ Redistributable yükle

## 🚀 Hızlı Test

### 1. **Geliştirme Modunda Test**
```bash
# Geliştirme modunda başlat
npm run electron:dev
```

### 2. **Manuel Başlatma**
```bash
# 1. Backend'i başlat
cd backend
python -m uvicorn app.main:app --port 8000

# 2. Frontend'i başlat (yeni terminal)
cd frontend
npm run dev

# 3. Electron'u başlat (yeni terminal)
npm run electron
```

### 3. **Log Kontrolü**
```bash
# Electron loglarını kontrol et
# Windows: %APPDATA%\autosniper-desktop\logs\
```

## 📋 Kontrol Listesi

- [ ] Python 3.11+ kurulu mu?
- [ ] Node.js 18+ kurulu mu?
- [ ] Tüm kütüphaneler yüklü mü?
- [ ] Port 8000 serbest mi?
- [ ] Antivirüs engellemiyor mu?
- [ ] Windows güncel mi?

## 🆘 Yardım

Sorun devam ederse:
1. **Ekran görüntüsü** alın
2. **Hata mesajını** kopyalayın
3. **Windows sürümünü** belirtin
4. **Log dosyalarını** paylaşın

---

*AutoSniper Teknik Destek*
