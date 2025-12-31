# Yerel Kurulum Rehberi

## Gereksinimler

### 1. Python 3.11+
- Python'un yüklü olduğunu kontrol edin: `python --version`
- Yüklü değilse: https://www.python.org/downloads/

### 2. Node.js 18+
- Node.js'in yüklü olduğunu kontrol edin: `node --version`
- Yüklü değilse: https://nodejs.org/

### 3. PostgreSQL
- PostgreSQL'in yüklü olduğunu kontrol edin: `psql --version`
- Yüklü değilse: https://www.postgresql.org/download/windows/
- Veya Docker ile sadece PostgreSQL'i çalıştırın: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=autosniper postgres:15-alpine`

## Kurulum Adımları

### Backend Kurulumu

1. **Backend klasörüne gidin:**
```bash
cd backend
```

2. **Virtual environment oluşturun:**
```bash
python -m venv venv
```

3. **Virtual environment'ı aktifleştirin:**
```bash
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
venv\Scripts\activate.bat

# Mac/Linux:
source venv/bin/activate
```

4. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

5. **Playwright tarayıcılarını yükleyin:**
```bash
playwright install chromium
```

6. **Environment değişkenlerini ayarlayın:**
`backend/.env` dosyası oluşturun:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/autosniper
SECRET_KEY=your-secret-key-change-in-production-use-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
SCRAPER_INTERVAL_SECONDS=30
```

7. **Veritabanını oluşturun:**
```bash
# PostgreSQL'e bağlanın ve veritabanı oluşturun
psql -U postgres
CREATE DATABASE autosniper;
\q
```

8. **Backend'i başlatın:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Kurulumu

1. **Yeni bir terminal açın ve frontend klasörüne gidin:**
```bash
cd frontend
```

2. **Bağımlılıkları yükleyin:**
```bash
npm install
```

3. **Environment değişkenlerini ayarlayın:**
`frontend/.env` dosyası oluşturun:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

4. **Frontend'i başlatın:**
```bash
npm run dev
```

## Çalıştırma

1. **PostgreSQL'in çalıştığından emin olun**
2. **Backend terminalinde:** `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. **Frontend terminalinde:** `npm run dev`
4. **Tarayıcıda:** http://localhost:3000 (veya Vite'ın gösterdiği port)

## Sorun Giderme

### PostgreSQL bağlantı hatası
- PostgreSQL servisinin çalıştığından emin olun
- `DATABASE_URL`'deki şifrenin doğru olduğundan emin olun

### Port zaten kullanılıyor
- 8000 portu kullanılıyorsa: `netstat -ano | findstr :8000` ile hangi process'in kullandığını bulun
- 3000 portu kullanılıyorsa Vite otomatik olarak başka bir port seçecektir

### CORS hatası
- Backend'in `CORS_ORIGINS` ayarında frontend'in çalıştığı portun olduğundan emin olun
- Backend'i yeniden başlatın

