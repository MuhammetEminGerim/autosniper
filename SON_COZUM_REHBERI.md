# AutoSniper Son Çözüm Rehberi

## 🚨 **Sorun: Program Açılmıyor, CMD Kapanıyor**

## 🔧 **Denenmiş Çözümler:**
- ✅ Port 8000 → 8001 → 8002 değiştirildi
- ✅ Hata mesajları eklendi
- ✅ Bekleme süresi artırıldı
- ✅ Debug script'leri oluşturuldu

## 🎯 **En Garanti Çözüm:**

### **1. Geliştirme Modunda Çalıştır**
```bash
DEV_MODE_8002.bat
```
Bu komut:
- Backend'i port 8002'de başlatır
- Frontend'i geliştirme modunda çalıştırır
- Electron'u manuel başlatır
- Hataları net gösterir

### **2. Manuel Başlatma**
```bash
# Terminal 1:
cd backend
python -m uvicorn app.main:app --port 8002

# Terminal 2 (5 saniye sonra):
cd frontend
npm run dev

# Terminal 3 (3 saniye sonra):
set BACKEND_URL=http://localhost:8002
npm run electron
```

## 🔍 **Sorun Tespiti:**

### **Backend Çalışıyor mu?**
```bash
cd backend
python -m uvicorn app.main:app --port 8002
```
- Hata verirse: Python kütüphaneleri eksik
- Çalışırsa: Backend OK

### **Frontend Çalışıyor mu?**
```bash
cd frontend
npm run dev
```
- http://localhost:3000 açılıyorsa: Frontend OK

### **Electron Çalışıyor mu?**
```bash
npm run electron
```
- Pencere açılıyorsa: Electron OK

## 📋 **Son Kontrol Listesi:**

- [ ] `DEV_MODE_8002.bat` çalıştırıldı mı?
- [ ] Backend hata vermedi mi?
- [ ] Frontend açıldı mı?
- [ ] Electron penceresi çıktı mı?

## 🆘 **Hala Çalışmıyorsa:**

### **En Basit Çözüm:**
1. **Python 3.11** kurun (3.13 sorun çıkarabilir)
2. **Node.js 18** kurun
3. **Visual Studio Code** yeniden başlatın
4. **Windows'u** yeniden başlatın

### **Alternatif:**
- Geliştirme modunda kullanmaya devam edin
- `npm run electron:dev` komutu en stabilidir

---

**Not: Port 8002'de program çalışıyorsa, setup dosyası sorunu olabilir. Geliştirme modu kullanabilirsiniz.**
