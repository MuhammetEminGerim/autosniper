# AutoSniper - Araç Fırsat Yakalama Sistemi

AutoSniper, ikinci el araç piyasasındaki fırsatları herkesten önce yakalamayı sağlayan bir otomasyon (SaaS) sistemidir.

## 🎯 Özellikler

- **Akıllı Filtreleme**: Marka, model, yıl, fiyat, şehir gibi kriterlere göre özelleştirilebilir filtreler
- **7/24 İzleme**: Arka planda sürekli çalışan scraper servisi
- **Anlık Bildirimler**: WebSocket ile gerçek zamanlı bildirimler
- **Modern Dashboard**: Kullanıcı dostu arayüz
- **Sesli Uyarılar**: Tarayıcı bildirim API'si ile sesli uyarılar

## 🚀 Kurulum

### Gereksinimler

- Docker ve Docker Compose
- Node.js 18+ (geliştirme için)
- Python 3.11+ (geliştirme için)

### Docker ile Çalıştırma

1. Projeyi klonlayın:
```bash
git clone <repo-url>
cd sniper
```

2. Docker Compose ile tüm servisleri başlatın:
```bash
docker-compose up -d
```

3. Servisler hazır:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Dokümantasyonu: http://localhost:8000/docs

### Geliştirme Modu

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Playwright tarayıcılarını yükle
playwright install chromium

# Veritabanı bağlantısını ayarla (.env dosyası oluştur)
cp .env.example .env

# Uygulamayı başlat
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📁 Proje Yapısı

```
sniper/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoint'leri
│   │   ├── core/         # Config, security, database
│   │   ├── models/       # SQLAlchemy modelleri
│   │   ├── schemas/      # Pydantic şemaları
│   │   ├── services/     # İş mantığı
│   │   │   ├── scraper/  # Playwright scraper
│   │   │   └── websocket/ # WebSocket yönetimi
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React bileşenleri
│   │   ├── pages/        # Sayfa bileşenleri
│   │   ├── services/     # API ve WebSocket servisleri
│   │   └── store/        # Zustand state yönetimi
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Yapılandırma

### Backend Environment Variables

`.env` dosyası oluşturun:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/autosniper
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
SCRAPER_INTERVAL_SECONDS=30
```

### Frontend Environment Variables

`.env` dosyası oluşturun:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 📚 API Dokümantasyonu

Backend çalıştıktan sonra Swagger UI'ya erişebilirsiniz:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Kullanım

1. **Kayıt Ol**: http://localhost:3000/register adresinden hesap oluşturun
2. **Filtre Oluştur**: Dashboard'dan yeni filtre oluşturun
3. **İzle**: Sistem otomatik olarak ilanları taramaya başlar
4. **Bildirim Al**: Filtrelerinize uyan yeni ilanlar için anında bildirim alın

## 🔒 Güvenlik

- JWT token tabanlı kimlik doğrulama
- Şifreler bcrypt ile hash'lenir
- CORS koruması
- SQL injection koruması (SQLAlchemy ORM)

## 📝 Notlar

- Scraper servisi şu anda örnek implementasyon içeriyor. Gerçek kullanım için hedef sitenin yapısına göre güncellenmelidir.
- Production ortamında SECRET_KEY mutlaka değiştirilmelidir.
- Veritabanı migration'ları için Alembic kullanılabilir (şu anda otomatik tablo oluşturma kullanılıyor).

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add some amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje özel bir projedir.

