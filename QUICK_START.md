# Hızlı Başlangıç - Python 3.13 ile

## Python 3.13 Kurulumu Sonrası

### 1. Python'un Kurulu Olduğunu Kontrol Edin
```powershell
py --version
# veya
python --version
```

### 2. Backend Kurulumu

```powershell
cd backend

# Virtual environment oluştur
py -m venv venv

# Virtual environment'ı aktifleştir
.\venv\Scripts\Activate.ps1

# Pip'i güncelle
python -m pip install --upgrade pip

# Bağımlılıkları yükle
pip install -r requirements.txt

# Playwright tarayıcılarını yükle
playwright install chromium
```

### 3. Environment Dosyası Oluşturun

`backend/.env` dosyası oluşturun:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/autosniper
SECRET_KEY=your-secret-key-change-in-production-use-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
SCRAPER_INTERVAL_SECONDS=30
```

### 4. PostgreSQL Hazırlayın

Docker ile sadece PostgreSQL:
```powershell
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=autosniper --name autosniper-db postgres:15-alpine
```

Veya yerel PostgreSQL kullanıyorsanız:
```sql
CREATE DATABASE autosniper;
```

### 5. Backend'i Başlatın

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Frontend Kurulumu (Yeni Terminal)

```powershell
cd frontend

# Bağımlılıkları yükle
npm install

# .env dosyası oluşturun
# VITE_API_URL=http://localhost:8000
# VITE_WS_URL=ws://localhost:8000

# Frontend'i başlat
npm run dev
```

### 7. Tarayıcıda Açın

http://localhost:3000 (veya Vite'ın gösterdiği port)

## Sorun Giderme

### Paketler yüklenmiyorsa
- Python 3.13 için bazı paketler henüz wheel sağlamıyor olabilir
- Bu durumda Python 3.11 veya 3.12 kullanmanız gerekebilir
- Veya Docker ile devam edebilirsiniz

### C++ Build Tools Hatası
- Eğer "Microsoft Visual C++ 14.0" hatası alırsanız:
  - Visual Studio Build Tools kurun: https://visualstudio.microsoft.com/visual-cpp-build-tools/
  - Veya Python 3.11/3.12 kullanın (wheel'ler hazır)

