# AutoSniper Acil Sorun Giderme

## 🚨 **CMD Açılıp Kapanıyor Sorunu**

### **Hızlı Test Adımları:**

#### **1. Backend'i Manuel Test Et**
```bash
# 1. Terminal aç
# 2. Backend'i çalıştır
cd dist\win-unpacked\resources\backend
autosniper-backend.exe

# Hata çıkarsa 5 saniye bekleyip kapanıyorsa sorun backend'dedir
```

#### **2. Geliştirme Modunda Test Et**
```bash
# DEV_MODE.bat çalıştır
# veya manuel:
cd backend
python -m uvicorn app.main:app --port 8000

# Yeni terminal:
cd frontend  
npm run dev

# Yeni terminal:
npm run electron
```

#### **3. Debug Modunda Electron Çalıştır**
```bash
# DEBUG_ELECTRON.bat çalıştır
# veya:
cd dist\win-unpacked
AutoSniper.exe --enable-logging --v=1
```

## 🔍 **Muhtemel Nedenler:**

### **1. Backend Hatası**
- Backend exe'si hata veriyor olabilir
- Port 8000 başka uygulama tarafından kullanılıyor olabilir
- Python kütüphaneleri eksik olabilir

### **2. Electron Hatası**
- Frontend dosyaları eksik olabilir
- Electron crash ediyor olabilir

### **3. Sistem Sorunları**
- Windows Defender engelliyor olabilir
- Visual C++ Redistributable eksik olabilir

## 🛠️ **Çözüm Önerileri:**

### **Çözüm 1: Port Değiştir**
```python
# electron/main.js'de port değiştir
const BACKEND_PORT = 8001;  # 8000'den 8001'e değiştir
```

### **Çözüm 2: Geliştirme Modunda Çalış**
```bash
npm run electron:dev
```

### **Çözüm 3: Manuel Başlat**
```bash
# 1. Backend'i başlat
cd dist\win-unpacked\resources\backend
start autosniper-backend.exe

# 2. 3 saniye bekle
timeout 3

# 3. Electron'u başlat  
cd dist\win-unpacked
start AutoSniper.exe
```

## 📋 **Kontrol Listesi:**

- [ ] `autosniper-backend.exe` çalışıyor mu?
- [ ] Port 8000 serbest mi? (`netstat -ano | findstr :8000`)
- [ ] Frontend build edilmiş mi? (`frontend/dist` var mı?)
- [ ] Windows Defender engellemiyor mu?
- [ ] Log dosyalarında hata var mı?

## 🆘 **Hala Çözülmüyorsa:**

1. **Ekran görüntüsü** alın
2. **Hata mesajını** kopyalayın  
3. **Windows sürümünü** belirtin
4. **DEBUG_ELECTRON.bat** çıktısını paylaşın

---

*En hızlı çözüm: `npm run electron:dev` ile geliştirme modunda çalışın!*
