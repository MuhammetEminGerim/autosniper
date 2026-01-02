# AutoSniper Desktop App

**Paket program olarak satılabilir desktop uygulaması** - Offline lisans sistemi ile!

## 🎯 Proje Durumu

**İlerleme:** 71% (5/7 Phase Tamamlandı)

### ✅ Tamamlanan
- License System (offline validation)
- License API (activation, status)
- Electron Setup (window, tray, IPC)
- Backend Packaging (PyInstaller config)
- Frontend License UI (activation, expiry)

### ⏳ Kalan
- Build & Package (installer)
- Testing (cross-platform)

---

## 💰 İş Modeli

**Satış Paketleri:**
- Monthly: ₺49/ay (30 gün)
- Yearly: ₺299/yıl (365 gün)
- Lifetime: ₺999 (ömür boyu)

**Maliyet:** $0/ay (offline lisans)

---

## 🏗️ Mimari

```
AutoSniper Desktop
├── Electron (main.js, preload.js)
│   ├── Window management
│   ├── Backend subprocess
│   └── License storage
│
├── Frontend (React + Vite)
│   ├── LicenseActivation.tsx
│   ├── LicenseExpired.tsx
│   └── Dashboard
│
└── Backend (FastAPI + PyInstaller)
    ├── License API
    ├── Scraper
    └── SQLite
```

---

## 📦 Kullanıcı Deneyimi

1. **AutoSniper-Setup.exe** indir
2. Çift tıkla, kur
3. Lisans key gir
4. Kullan!

---

## 🚀 Development

### Backend Build
```bash
cd backend
python build.bat  # Windows
./build.sh        # Linux/Mac
```

### Electron Dev
```bash
npm run electron:dev
```

### Production Build
```bash
npm run build
npm run dist
```

---

## 📁 Önemli Dosyalar

**License System:**
- `backend/app/core/license.py` - Core logic
- `backend/app/api/license.py` - API endpoints
- `backend/app/models/license.py` - Database

**Electron:**
- `electron/main.js` - Main process
- `electron/preload.js` - IPC bridge
- `package.json` - Config

**Frontend:**
- `frontend/src/pages/LicenseActivation.tsx`
- `frontend/src/pages/LicenseExpired.tsx`

**Build:**
- `backend/backend.spec` - PyInstaller
- `backend/build.bat` - Build script

---

## 🎯 Sonraki Adımlar

1. App.tsx'e route ekle
2. Icon oluştur
3. Windows installer build
4. Test
5. Release!

---

**Geliştirme:** 2 gün  
**Durum:** Neredeyse hazır! 🚀
