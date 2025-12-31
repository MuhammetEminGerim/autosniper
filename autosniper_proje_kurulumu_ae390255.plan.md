# AutoSniper - Proje Kurulumu ve Dokümantasyon

## 📋 İçindekiler

1. [Proje Hakkında](#proje-hakkında)
2. [Mimari ve Teknolojiler](#mimari-ve-teknolojiler)
3. [Özellikler](#özellikler)
4. [Kurulum](#kurulum)
5. [Yapılandırma](#yapılandırma)
6. [Proje Yapısı](#proje-yapısı)
7. [Kullanım Kılavuzu](#kullanım-kılavuzu)
8. [API Dokümantasyonu](#api-dokümantasyonu)
9. [Bilinen Sorunlar ve Çözümler](#bilinen-sorunlar-ve-çözümler)
10. [Geliştirme Notları](#geliştirme-notları)

---

## 🎯 Proje Hakkında

**AutoSniper**, ikinci el araç piyasasındaki fırsatları otomatik olarak yakalayan bir SaaS (Software as a Service) sistemidir. Kullanıcılar, belirledikleri kriterlere göre özel filtreler oluşturabilir ve sistem 7/24 çalışarak yeni ilanları tarar, bildirim gönderir.

### Temel Kavramlar

- **Hızlı Tarama**: Kriter belirtmeden genel arama yapma
- **Özel Filtreler**: Kullanıcı tanımlı kriterlere göre otomatik tarama
- **Scheduler**: Belirli aralıklarla otomatik tarama yapan zamanlayıcı servisi
- **Favoriler**: İlanları kaydetme ve fiyat değişimi takibi
- **Karşılaştırma**: İlanları yan yana karşılaştırma

---

## 🏗️ Mimari ve Teknolojiler

### Backend Stack

- **Framework**: FastAPI 0.104.1
- **Dil**: Python 3.11+
- **ORM**: SQLAlchemy 2.0.23
- **Veritabanı**: PostgreSQL 15
- **Web Scraping**: Playwright 1.40.0 + BeautifulSoup4
- **Scheduler**: APScheduler 3.10.4
- **HTTP Client**: aiohttp 3.9.1
- **Kimlik Doğrulama**: JWT (python-jose)
- **Şifre Hash**: bcrypt (passlib)
- **API Dokümantasyonu**: OpenAPI/Swagger

### Frontend Stack

- **Framework**: React 18.2.0
- **Dil**: TypeScript 5.2.2
- **Build Tool**: Vite 5.0.0
- **Routing**: React Router DOM 6.20.0
- **State Management**: Zustand 4.4.7
- **HTTP Client**: Axios 1.6.2
- **UI Feedback**: React Hot Toast 2.4.1
- **Stil**: CSS3 (Glassmorphism, Animations)

### DevOps & Deployment

- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (production frontend)
- **WSGI Server**: Uvicorn (ASGI server)
- **Database**: PostgreSQL (Docker container)

---

## ✨ Özellikler

### 🔐 Kullanıcı Yönetimi

- ✅ Kullanıcı kayıt/giriş sistemi
- ✅ JWT token tabanlı kimlik doğrulama
- ✅ Şifre sıfırlama (Email token sistemi)
- ✅ Şifreler bcrypt ile hash'lenir
- ✅ Session yönetimi

### 🔍 Arama ve Filtreleme

- ✅ **Hızlı Tarama**: Kriter belirtmeden genel arama
- ✅ **Özel Filtreler**: 
  - Marka, Model
  - Yıl aralığı (min/max)
  - Fiyat aralığı (min/max)
  - Kilometre aralığı (min/max)
  - Şehir
  - Yakıt tipi (Benzin, Dizel, LPG, Elektrik, Hibrit)
  - Vites tipi (Manuel, Otomatik, Yarı Otomatik)
- ✅ Filtre düzenleme ve silme
- ✅ Filtre aktif/pasif yapma

### 🤖 Otomatik Tarama (Scheduler)

- ✅ Her filtre için ayrı tarama zamanlayıcı
- ✅ Özelleştirilebilir tarama sıklığı (30dk, 1 saat, 2 saat, 6 saat, 12 saat, 24 saat)
- ✅ Otomatik taramayı açma/kapama
- ✅ Son tarama zamanı takibi
- ✅ Toplam tarama sayısı istatistikleri
- ✅ Yeni bulunan ilan sayısı takibi

### 📊 İlan Yönetimi

- ✅ **Sekmeli Görünüm**:
  - Tümü (Tüm ilanlar)
  - Hızlı Tarama (Kriterlersiz aramalar)
  - Filtrelerimden (Özel filtrelerden gelen ilanlar)
- ✅ İlan detay sayfası
- ✅ İlan silme (tekli/toplu)
- ✅ Kaynak bazlı silme (tümü, hızlı tarama, filtreler)
- ✅ Sayfalama (pagination)
- ✅ Filtreleme (marka, şehir, fiyat)

### 📄 İlan Detayları

- ✅ İlan başlığı ve açıklama
- ✅ Fiyat bilgisi
- ✅ Görsel galeri (thumbnail navigation)
- ✅ Hızlı özellikler (Yıl, KM, Yakıt, Vites, Şehir)
- ✅ **Hasar Diyagramı (Tramer)**:
  - SVG tabanlı araç hasar görselleştirme
  - Orijinal/Boyalı/Lokal Boyalı/Değişen parçalar
  - Tramer tutarı bilgisi
  - Parça bazlı hasar listesi
  - Ticari araçlarda hasar bilgisi yoksa bilgilendirme
- ✅ Detaylı özellikler
- ✅ Kaynak URL

### ❤️ Favoriler

- ✅ İlanları favorilere ekleme/çıkarma
- ✅ Favori listesi görüntüleme
- ✅ **Fiyat Değişimi Takibi**:
  - İlk fiyat kaydı
  - Güncel fiyat takibi
  - Fiyat değişimi gösterimi
  - Fiyat düşüşü yüzdesi
  - Fiyat geçmişi

### ⚖️ İlan Karşılaştırma

- ✅ İlanları karşılaştırma listesine ekleme
- ✅ Yan yana karşılaştırma görünümü
- ✅ Fiyat, kilometre, hasar durumu karşılaştırması
- ✅ Farkları vurgulama

### 📊 İstatistikler Dashboard

- ✅ **Piyasa İstatistikleri**:
  - Toplam ilan sayısı
  - Ortalama fiyat
  - En düşük/en yüksek fiyat
  - Ortalama yıl
  - Ortalama kilometre
  - Son 24 saatte eklenen ilanlar
  - 7 günlük fiyat değişimi trendi
- ✅ **Marka Dağılımı**: En popüler markalar ve yüzdeleri
- ✅ **Şehir Dağılımı**: En çok ilan olan şehirler
- ✅ **Fiyat Dağılımı**: Fiyat aralıklarına göre grafik

### 🔔 Bildirimler

- ✅ **Telegram Bildirimleri** (%100 Ücretsiz):
  - Yeni ilan bildirimi
  - Fiyat düşüşü bildirimi
  - Bot token yapılandırması
  - Chat ID yönetimi
  - Test mesajı gönderme
- ✅ **Tarayıcı Push Bildirimleri**:
  - Yeni ilan bildirimi
  - Fiyat düşüşü bildirimi
  - İzin yönetimi
  - Test bildirimi

### 🎨 Kullanıcı Arayüzü

- ✅ Modern dark theme tasarım
- ✅ Glassmorphism efektleri
- ✅ Responsive tasarım (Mobil uyumlu)
- ✅ Animasyonlar (fadeIn, stagger, float, gradient shift)
- ✅ Skeleton loading
- ✅ Toast bildirimleri
- ✅ Sidebar navigation (Desktop/Mobil)
- ✅ Lazy loading images
- ✅ Touch-friendly butonlar

### 🛡️ Güvenlik

- ✅ JWT token tabanlı authentication
- ✅ Şifreler bcrypt ile hash
- ✅ CORS koruması
- ✅ SQL injection koruması (SQLAlchemy ORM)
- ✅ Password reset token sistemi
- ✅ Token expire yönetimi

### ⚙️ Performans ve Optimizasyon

- ✅ Database indexing (fiyat, yıl, yakıt, kilometre, tarih)
- ✅ Composite indexes (marka+fiyat, şehir+fiyat)
- ✅ Lazy loading images
- ✅ Connection pooling (aiohttp)
- ✅ Rate limiting (Semaphore)
- ✅ Paralel scraping (asyncio.gather)
- ✅ Otomatik eski ilan temizliği (30 günden eski)
- ✅ Browser memory leak önleme

---

## 🚀 Kurulum

### Gereksinimler

- **Docker** ve **Docker Compose** (Önerilen)
- VEYA
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+**

### Docker ile Hızlı Kurulum (Önerilen)

1. **Projeyi klonlayın:**
```bash
git clone <repo-url>
cd sniper
```

2. **Environment değişkenlerini ayarlayın:**

`.env` dosyası oluşturun (opsiyonel - docker-compose.yml'de varsayılanlar var):
```env
# Telegram Bot (Opsiyonel)
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

3. **Docker Compose ile tüm servisleri başlatın:**
```bash
docker-compose up -d --build
```

4. **Servisler hazır:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Dokümantasyonu: http://localhost:8000/docs
   - PostgreSQL: localhost:5432

5. **Logları kontrol edin:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Manuel Kurulum

#### Backend Kurulumu

1. **Backend klasörüne gidin:**
```bash
cd backend
```

2. **Virtual environment oluşturun:**
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

3. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

4. **Playwright tarayıcılarını yükleyin:**
```bash
playwright install chromium
```

5. **Environment değişkenlerini ayarlayın:**

`backend/.env` dosyası oluşturun:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/autosniper
SECRET_KEY=your-secret-key-change-in-production-use-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
SCRAPER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_optional
```

6. **Veritabanını oluşturun:**
```bash
# PostgreSQL'e bağlanın
psql -U postgres

# Veritabanı oluşturun
CREATE DATABASE autosniper;
\q
```

7. **Backend'i başlatın:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Kurulumu

1. **Yeni terminal açın ve frontend klasörüne gidin:**
```bash
cd frontend
```

2. **Bağımlılıkları yükleyin:**
```bash
npm install
```

3. **Environment değişkenlerini ayarlayın:**

`frontend/.env` dosyası oluşturun (opsiyonel - varsayılanlar var):
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

4. **Frontend'i başlatın:**
```bash
npm run dev
```

5. **Tarayıcıda açın:**
   - http://localhost:3000 (veya Vite'ın gösterdiği port)

---

## ⚙️ Yapılandırma

### Docker Compose Yapılandırması

`docker-compose.yml` dosyasında şu servisler tanımlıdır:

- **db**: PostgreSQL 15 Alpine
- **backend**: FastAPI uygulaması
- **frontend**: React uygulaması (Nginx ile serve edilir)

### Backend Environment Variables

| Değişken | Açıklama | Varsayılan |
|----------|----------|------------|
| `DATABASE_URL` | PostgreSQL bağlantı string'i | `postgresql://postgres:postgres@db:5432/autosniper` |
| `SECRET_KEY` | JWT token şifreleme anahtarı | `your-secret-key-change-in-production` |
| `CORS_ORIGINS` | CORS izin verilen origin'ler | `http://localhost:3000,...` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (opsiyonel) | - |
| `SCRAPER_USER_AGENT` | Web scraper user agent | Mozilla/5.0... |

### Frontend Environment Variables

| Değişken | Açıklama | Varsayılan |
|----------|----------|------------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_WS_URL` | WebSocket URL | `ws://localhost:8000` |

---

## 📁 Proje Yapısı

```
sniper/
├── backend/
│   ├── app/
│   │   ├── api/                    # API endpoint'leri
│   │   │   ├── auth.py            # Kimlik doğrulama (login, register, password reset)
│   │   │   ├── filters.py         # Filtre CRUD ve scheduler
│   │   │   ├── listings.py        # İlan listeleme, detay, silme, istatistikler
│   │   │   ├── favorites.py       # Favoriler yönetimi
│   │   │   ├── settings.py        # Ayarlar (Telegram)
│   │   │   ├── test.py            # Test endpoint'leri (scraping)
│   │   │   ├── websocket.py       # WebSocket bağlantıları
│   │   │   └── dependencies.py    # Dependency injection
│   │   ├── core/
│   │   │   ├── config.py          # Ayarlar yönetimi
│   │   │   ├── database.py        # Database bağlantısı
│   │   │   └── security.py        # JWT ve password hashing
│   │   ├── models/                 # SQLAlchemy modelleri
│   │   │   ├── user.py            # Kullanıcı modeli
│   │   │   ├── filter.py          # Filtre modeli
│   │   │   ├── listing.py         # İlan modeli
│   │   │   └── favorite.py        # Favori modeli
│   │   ├── schemas/                # Pydantic şemaları
│   │   │   ├── user.py
│   │   │   ├── filter.py
│   │   │   ├── listing.py
│   │   │   └── favorite.py
│   │   ├── services/
│   │   │   ├── scraper/
│   │   │   │   ├── scraper.py     # Playwright ile web scraping
│   │   │   │   └── worker.py      # Scraper worker (kullanılmıyor)
│   │   │   ├── scheduler/
│   │   │   │   └── scheduler_service.py  # APScheduler servisi
│   │   │   ├── telegram/
│   │   │   │   └── telegram_service.py   # Telegram bot bildirimleri
│   │   │   └── websocket/
│   │   │       └── manager.py     # WebSocket bağlantı yönetimi
│   │   └── main.py                 # FastAPI uygulaması
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/             # React bileşenleri
│   │   │   ├── Layout.tsx         # Ana layout (sidebar)
│   │   │   ├── Layout.css
│   │   │   ├── ProtectedRoute.tsx # Route koruma
│   │   │   ├── Skeleton.tsx       # Loading skeleton
│   │   │   └── CarDamageDiagram.tsx  # Hasar diyagramı SVG
│   │   ├── pages/                  # Sayfa bileşenleri
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── ForgotPassword.tsx
│   │   │   ├── ResetPassword.tsx
│   │   │   ├── Dashboard.tsx      # Ana dashboard
│   │   │   ├── Search.tsx         # Hızlı tarama
│   │   │   ├── MyFilters.tsx      # Filtre yönetimi
│   │   │   ├── Listings.tsx       # İlan listesi (sekmeli)
│   │   │   ├── ListingDetail.tsx  # İlan detay
│   │   │   ├── Favorites.tsx      # Favoriler
│   │   │   ├── Compare.tsx        # İlan karşılaştırma
│   │   │   ├── Statistics.tsx     # İstatistikler
│   │   │   └── Settings.tsx       # Ayarlar
│   │   ├── services/
│   │   │   ├── api.ts             # Axios API client
│   │   │   └── pushNotifications.ts  # Browser push notifications
│   │   ├── store/                  # Zustand state management
│   │   │   ├── authStore.ts       # Authentication state
│   │   │   └── compareStore.ts    # Karşılaştırma state
│   │   ├── App.tsx                 # Ana uygulama component
│   │   └── index.css               # Global stiller
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml              # Docker Compose yapılandırması
├── README.md
└── autosniper_proje_kurulumu_ae390255.plan.md  # Bu dosya
```

---

## 📖 Kullanım Kılavuzu

### İlk Kurulum Sonrası

1. **Hesap Oluşturma:**
   - http://localhost:3000/register adresinden kayıt olun
   - Email ve şifre belirleyin

2. **Giriş Yapma:**
   - http://localhost:3000/login adresinden giriş yapın

### Filtre Oluşturma

1. **Filtrelerim** sayfasına gidin
2. **"Yeni Filtre Oluştur"** butonuna tıklayın
3. Filtre adı girin
4. Kriterler belirleyin (marka, model, yıl, fiyat, km, şehir, yakıt, vites)
5. Otomatik tarama ayarlarını yapın:
   - Otomatik taramayı aktifleştirin
   - Tarama sıklığını seçin (30dk - 24 saat)
6. **"Filtre Oluştur"** butonuna tıklayın

### Hızlı Tarama

1. **Arama** sayfasına gidin
2. İstediğiniz kriterleri girin (opsiyonel)
3. **"Ara"** butonuna tıklayın
4. Sonuçlar **İlanlar** sayfasında **"Hızlı Tarama"** sekmesinde görünecek

### İlan Görüntüleme

1. **İlanlar** sayfasına gidin
2. Sekmelerden birini seçin:
   - **Tümü**: Tüm ilanlar
   - **Hızlı Tarama**: Kriterlersiz aramalardan gelen ilanlar
   - **Filtrelerimden**: Özel filtrelerden gelen ilanlar
3. İlan kartına tıklayarak detay sayfasına gidin

### Favorilere Ekleme

1. İlan detay sayfasında **"❤️ Favorilere Ekle"** butonuna tıklayın
2. **Favoriler** sayfasından favori ilanlarınızı görüntüleyin
3. Fiyat değişiklikleri otomatik olarak takip edilir

### İlan Karşılaştırma

1. İlan detay sayfasında **"⚖️ Karşılaştır"** butonuna tıklayın
2. Karşılaştırmak istediğiniz diğer ilanları da ekleyin
3. **Karşılaştır** sayfasından yan yana karşılaştırın

### Telegram Bildirimleri

1. **Ayarlar** sayfasına gidin
2. **Telegram Bildirimleri** bölümüne gidin
3. Telegram bot token'ınızı backend'e ekleyin (docker-compose.yml veya .env)
4. Telegram'da @BotFather'dan bot oluşturun ve token alın
5. @userinfobot'a /start yazarak Chat ID'nizi öğrenin
6. Chat ID'nizi ayarlara girin
7. **"Bildirimleri Etkinleştir"** toggle'ını açın
8. **"Test Mesajı Gönder"** ile test edin

### Tarayıcı Bildirimleri

1. **Ayarlar** sayfasına gidin
2. **Tarayıcı Bildirimleri** bölümüne gidin
3. **"Bildirimleri Etkinleştir"** butonuna tıklayın
4. Tarayıcı izin isteğini onaylayın
5. **"Test Bildirimi"** ile test edin

---

## 📡 API Dokümantasyonu

Backend çalıştıktan sonra:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Ana Endpoint'ler

#### Authentication (`/api/auth`)
- `POST /register` - Kullanıcı kaydı
- `POST /login` - Giriş (JWT token döner)
- `POST /forgot-password` - Şifre sıfırlama isteği
- `POST /reset-password` - Şifre sıfırlama
- `GET /verify-reset-token/{token}` - Token doğrulama

#### Filters (`/api/filters`)
- `GET /` - Kullanıcının filtrelerini listele
- `POST /` - Yeni filtre oluştur
- `GET /{filter_id}` - Filtre detayı
- `PUT /{filter_id}` - Filtre güncelle
- `DELETE /{filter_id}` - Filtre sil
- `POST /{filter_id}/search` - Filtre ile manuel arama
- `PUT /{filter_id}/scheduler` - Scheduler ayarlarını güncelle
- `GET /scheduler/status` - Scheduler durumu
- `GET /scheduler/all-status` - Tüm scheduler istatistikleri

#### Listings (`/api/listings`)
- `GET /` - İlanları listele (sayfalama, filtreleme, kaynak bazlı)
- `GET /{listing_id}` - İlan detayı
- `GET /statistics` - Piyasa istatistikleri
- `DELETE /{listing_id}` - İlan sil
- `DELETE /` - Toplu ilan silme (kaynak bazlı)

#### Favorites (`/api/favorites`)
- `GET /` - Favori ilanları listele
- `POST /{listing_id}` - Favorilere ekle
- `DELETE /{listing_id}` - Favorilerden çıkar

#### Settings (`/api/settings`)
- `GET /telegram` - Telegram ayarlarını getir
- `PUT /telegram` - Telegram ayarlarını güncelle
- `POST /telegram/test` - Test mesajı gönder
- `GET /telegram/bot-info` - Bot bilgilerini getir

#### Test (`/api/test`)
- `POST /scrape` - Manuel scraping testi

---

## ⚠️ Bilinen Sorunlar ve Çözümler

### 1. arabam.com Bot Koruması (503 Hatası)

**Sorun**: arabam.com bazen bot/scraper isteklerini engelliyor ve 503 "Backend fetch failed" hatası veriyor.

**Çözümler**:
- Birkaç saat sonra tekrar deneyin (bot koruması geçici olabilir)
- Daha basit filtrelerle deneyin
- Scraper'da bot tespitini aşmak için stealth ayarları mevcut ama %100 garantili değil

**Durum**: Bu, hedef sitenin güvenlik politikası nedeniyle beklenen bir durumdur. Production'da proxy veya daha gelişmiş bot bypass teknikleri gerekebilir.

### 2. Playwright Timeout Hataları

**Sorun**: Sayfa yükleme sırasında timeout hataları oluşabiliyor.

**Çözüm**: Timeout süreleri artırıldı (90 saniye). Eğer sorun devam ederse:
- İnternet bağlantınızı kontrol edin
- arabam.com'un erişilebilir olduğundan emin olun

### 3. Database Connection Hataları

**Sorun**: Backend başlatılırken database bağlantı hatası.

**Çözüm**:
```bash
# Docker ile çalışıyorsanız:
docker-compose restart db

# Manuel çalışıyorsanız:
# PostgreSQL servisinin çalıştığından emin olun
```

### 4. CORS Hataları

**Sorun**: Frontend'den API çağrıları CORS hatası veriyor.

**Çözüm**: `backend/app/core/config.py` veya `docker-compose.yml`'de `CORS_ORIGINS` ayarını kontrol edin.

### 5. Telegram Bot Çalışmıyor

**Sorun**: Telegram bildirimleri gelmiyor.

**Çözüm**:
- Bot token'ının doğru ayarlandığından emin olun
- Chat ID'nin doğru olduğundan emin olun
- Botunuza /start yazdığınızdan emin olun
- Backend loglarını kontrol edin: `docker-compose logs backend | grep telegram`

---

## 🔧 Geliştirme Notları

### Database Schema

Veritabanı tabloları otomatik olarak oluşturulur (`Base.metadata.create_all`). Production'da Alembic migration kullanılması önerilir.

### Scraper Mimarisi

- Playwright ile headless browser kullanılır
- BeautifulSoup ile HTML parsing yapılır
- Paralel istekler için asyncio.gather kullanılır
- Rate limiting için Semaphore kullanılır
- Connection pooling için aiohttp ClientSession kullanılır

### Scheduler Servisi

- APScheduler ile zamanlanmış görevler yönetilir
- Her dakika aktif filtreler kontrol edilir
- Her 24 saatte bir eski ilanlar temizlenir (30 günden eski)
- Her 6 saatte bir favori fiyatları kontrol edilir

### Frontend State Management

- Zustand ile basit state management
- AuthStore: Authentication state
- CompareStore: Karşılaştırma state
- Local state: Component bazlı state (useState)

### Stil Yaklaşımı

- CSS modülleri kullanılır (her component için ayrı CSS)
- CSS variables ile tema yönetimi
- Glassmorphism efektleri
- Animations: fadeIn, stagger, float, gradient shift
- Responsive: Mobile-first yaklaşım

### Performance Optimizations

- Database indexing (fiyat, yıl, yakıt, kilometre, tarih)
- Composite indexes (marka+fiyat, şehir+fiyat)
- Lazy loading images
- Connection pooling
- Rate limiting
- Paralel processing
- Otomatik cleanup (eski ilanlar)

### Güvenlik Best Practices

- JWT token kullanımı
- Password hashing (bcrypt)
- SQL injection koruması (ORM)
- CORS yapılandırması
- Input validation (Pydantic)
- Token expiration

### Production Deployment Önerileri

1. **Environment Variables**: Tüm hassas bilgileri environment variable olarak saklayın
2. **SECRET_KEY**: Mutlaka güçlü bir secret key kullanın
3. **Database**: Production database kullanın (managed PostgreSQL)
4. **SSL/TLS**: HTTPS kullanın
5. **Rate Limiting**: API rate limiting ekleyin
6. **Monitoring**: Logging ve monitoring ekleyin
7. **Backup**: Database backup stratejisi oluşturun
8. **Scaling**: Load balancer ve multiple instances
9. **CDN**: Static assets için CDN kullanın
10. **Error Tracking**: Sentry gibi error tracking ekleyin

---

## 📝 Son Güncelleme

**Tarih**: 2024 (Güncel)
**Versiyon**: 1.0.0
**Durum**: Production'a hazır (bot koruması sorunu hariç)

### Tamamlanan Özellikler

✅ Tüm temel özellikler tamamlandı
✅ UI/UX modernizasyonu yapıldı
✅ Mobil uyumluluk eklendi
✅ Telegram bildirimleri eklendi
✅ Push notifications eklendi
✅ İstatistik dashboard eklendi
✅ İlan karşılaştırma eklendi
✅ Fiyat değişimi takibi eklendi
✅ Şifre sıfırlama eklendi
✅ Performans optimizasyonları yapıldı

### Bilinen Kısıtlamalar

⚠️ arabam.com bot koruması nedeniyle scraping bazen başarısız olabilir
⚠️ Production'da Alembic migration kullanılması önerilir
⚠️ Rate limiting eklenmemiş (production için önerilir)

---

## 📞 Destek ve Katkı

Sorunlar için:
- GitHub Issues kullanın
- Backend loglarını kontrol edin: `docker-compose logs backend`
- Frontend loglarını kontrol edin: Browser Developer Console

---

**Not**: Bu dokümantasyon projenin mevcut durumunu yansıtmaktadır. Güncellemeler yapıldıkça bu dosya da güncellenmelidir.

